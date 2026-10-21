function siteRefInstall() {
  // Pass this whole file as the `function` argument of chrome-devtools `evaluate_script`.
  // It installs window.__siteRef and stores its own source in sessionStorage, so after a
  // same-origin navigation it can be reinstalled with:
  //   () => (0, eval)('(' + sessionStorage.getItem('__siteRefSrc') + ')')()
  try { sessionStorage.setItem('__siteRefSrc', siteRefInstall.toString()); } catch (error) { /* storage blocked: paste the file again */ }

  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

  const isVisible = el => {
    const rect = el.getBoundingClientRect();
    if (rect.width < 1 || rect.height < 1) return false;
    const style = getComputedStyle(el);
    return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > 0.01;
  };

  // Inactive tab panels / slides are often moved sideways and clipped by an ancestor's overflow,
  // so count only the width that is inside the viewport and every clipping ancestor.
  const isInViewportX = el => {
    const rect = el.getBoundingClientRect();
    if (rect.width < 1) return false;
    let left = Math.max(rect.left, 0);
    let right = Math.min(rect.right, window.innerWidth);
    for (let parent = el.parentElement; parent && parent !== document.body && right > left; parent = parent.parentElement) {
      if (getComputedStyle(parent).overflowX === 'visible') continue;
      const box = parent.getBoundingClientRect();
      left = Math.max(left, box.left);
      right = Math.min(right, box.right);
    }
    // Compare with the viewport too, so wide carousel tracks that fill the screen still count.
    return right - left >= Math.min(rect.width, window.innerWidth) * 0.5;
  };

  // Absolutely positioned backgrounds (blurs, gradients) are decoration, not layout blocks.
  const isDecoration = el => getComputedStyle(el).position === 'absolute'
    && !cleanText(el.innerText, 1) && !el.querySelector('img, picture, video, canvas, svg, iframe');

  const pageTop = el => el.getBoundingClientRect().top + window.scrollY;

  const describe = el => ({
    tag: el.tagName.toLowerCase(),
    id: el.id || undefined,
    className: (typeof el.className === 'string' ? el.className : '').trim().split(/\s+/).slice(0, 4).join(' ') || undefined,
  });

  const toHex = value => {
    const match = value && value.match(/rgba?\(([^)]+)\)/);
    if (!match) return null;
    const [r, g, b, a = 1] = match[1].split(/[\s,/]+/).filter(Boolean).map(Number);
    if (a === 0) return null;
    const hex = '#' + [r, g, b].map(n => Math.round(n).toString(16).padStart(2, '0')).join('');
    return a < 1 ? `${hex} / ${Math.round(a * 100)}%` : hex;
  };

  const tally = () => {
    const map = new Map();
    return {
      add(key, weight = 1) { if (key) map.set(key, (map.get(key) || 0) + weight); },
      top(n) { return [...map.entries()].sort((a, b) => b[1] - a[1]).slice(0, n).map(([value, count]) => ({ value, count })); },
    };
  };

  const cleanText = (text, max) => (text || '').trim().replace(/\s+/g, ' ').slice(0, max);

  // Elements stuck to the viewport top (headers) break full-page screenshots, so make them static.
  const unstickHeaders = () => {
    const changed = [];
    const others = [];
    for (const el of document.querySelectorAll('body *')) {
      const style = getComputedStyle(el);
      if (style.position !== 'fixed' && style.position !== 'sticky') continue;
      if (!isVisible(el)) continue;
      const rect = el.getBoundingClientRect();
      const isTopBar = rect.top <= 5 && rect.width >= window.innerWidth * 0.8 && rect.height < 260;
      if (isTopBar) {
        el.style.setProperty('position', 'relative', 'important');
        el.style.setProperty('top', 'auto', 'important');
        changed.push(describe(el));
      } else {
        others.push({ ...describe(el), position: style.position, rect: [rect.x, rect.y, rect.width, rect.height].map(Math.round) });
      }
    }
    return { changed, others };
  };

  const REVEAL_CSS = `
    .elementor-invisible { visibility: visible !important; }
    [data-aos] { opacity: 1 !important; transform: none !important; transition: none !important; }
    .wow, .animate__animated { visibility: visible !important; animation: none !important; opacity: 1 !important; }
  `;

  const visibleChildren = el => [...el.children].filter(child =>
    isVisible(child) && isInViewportX(child) && !['SCRIPT', 'STYLE', 'LINK', 'NOSCRIPT'].includes(child.tagName));

  // Top-level layout blocks; shared by sections(), links() and inspect().
  const topBlocks = selector => {
    if (selector) return [...document.querySelectorAll(selector)].filter(el => isVisible(el) && isInViewportX(el));
    let root = document.body;
    // Descend through single-child wrappers (#page, .site, #app ...).
    for (let i = 0; i < 10; i += 1) {
      const children = visibleChildren(root);
      if (children.length !== 1) break;
      root = children[0];
    }
    let blocks = visibleChildren(root);
    const total = document.scrollingElement.scrollHeight;
    // Expand any block that holds most of the page (usually <main> / #content) into its children.
    // Page builders nest deeply (e.g. .site-content > .container > main > article > .entry-content > .elementor).
    for (let pass = 0; pass < 15; pass += 1) {
      const next = [];
      let expanded = false;
      for (const block of blocks) {
        const children = visibleChildren(block);
        const isHeaderOrFooter = /^(HEADER|FOOTER)$/.test(block.tagName) || /header|footer/i.test(block.id + ' ' + block.className);
        if (!isHeaderOrFooter && block.offsetHeight > total * 0.5 && children.length >= 1) {
          next.push(...children);
          expanded = true;
        } else {
          next.push(block);
        }
      }
      blocks = next;
      if (!expanded) break;
    }
    return blocks
      .filter(el => el.offsetHeight >= 8 && getComputedStyle(el).position !== 'fixed' && !isDecoration(el))
      .sort((a, b) => pageTop(a) - pageTop(b));
  };

  window.__siteRef = {
    // scroll: false skips the scroll-through. Use it on scroll-driven pages, where jumping to the
    // bottom and back can leave the page's own animation state broken (see capture-gotchas.md).
    async prepare({ scroll = true, step = 600, delay = 250, unstick = true, hide = [], maxWaitMs = 10000 } = {}) {
      // 1. Scroll through the page so lazy images and scroll-triggered animations fire.
      if (scroll) {
        let lastHeight = 0;
        for (let i = 0, y = 0; i < 300; i += 1, y += step) {
          window.scrollTo(0, y);
          await sleep(delay);
          const height = document.scrollingElement.scrollHeight;
          if (y + window.innerHeight >= height && height === lastHeight) break;
          lastHeight = height;
        }
      }
      // 2. Force elements still waiting for their entrance animation to show.
      document.querySelectorAll('.elementor-invisible').forEach(el => el.classList.remove('elementor-invisible'));
      document.querySelectorAll('[data-aos]').forEach(el => el.classList.add('aos-animate'));
      const style = document.createElement('style');
      style.dataset.siteRef = 'reveal';
      style.textContent = REVEAL_CSS + hide.map(selector => `${selector}{display:none!important}`).join('\n');
      document.head.appendChild(style);
      // 3. Lazy images that only swap data-src on intersection.
      document.querySelectorAll('img[loading="lazy"]').forEach(img => { img.loading = 'eager'; });
      document.querySelectorAll('img[data-src]').forEach(img => {
        if (!img.getAttribute('src') || img.getAttribute('src').startsWith('data:')) img.src = img.dataset.src;
      });
      const fixed = unstick ? unstickHeaders() : { changed: [], others: [] };
      // 4. Back to top and wait for images and fonts.
      window.scrollTo(0, 0);
      const started = Date.now();
      let pending = [];
      while (Date.now() - started < maxWaitMs) {
        pending = [...document.images].filter(img => isVisible(img) && !img.complete);
        if (pending.length === 0) break;
        await sleep(300);
      }
      await Promise.race([document.fonts.ready, sleep(3000)]);
      await sleep(400);
      return {
        url: location.href,
        title: document.title,
        viewport: `${window.innerWidth}x${window.innerHeight}`,
        pageHeight: document.scrollingElement.scrollHeight,
        unstuckHeaders: fixed.changed,
        fixedElements: fixed.others,
        pendingImages: pending.slice(0, 10).map(img => img.currentSrc || img.src),
      };
    },

    // Signals that the page is scroll-driven, in which case a full-page screenshot will be wrong.
    inspect() {
      const viewportHeight = window.innerHeight;
      const blocks = topBlocks();
      const libraries = Object.entries({
        gsap: window.gsap, ScrollTrigger: window.ScrollTrigger, Lenis: window.Lenis, fullpage: window.fullpage_api,
        locomotive: document.querySelector('[data-scroll-container]'), skrollr: window.skrollr,
      }).filter(([, value]) => value).map(([name]) => name);
      const pinned = document.querySelectorAll('.pin-spacer, [data-pin], [data-scroll-sticky]').length;
      const tallWithSticky = blocks.filter(block => block.offsetHeight > viewportHeight * 3
        && [...block.querySelectorAll('*')].some(el => /sticky|fixed/.test(getComputedStyle(el).position)))
        .map(block => ({ ...describe(block), height: block.offsetHeight }));
      const screenSized = blocks.filter(block => Math.abs(block.offsetHeight - viewportHeight) <= 2).length;
      const hiddenUntilScrolled = [...document.querySelectorAll('body *')].filter(el => {
        const rect = el.getBoundingClientRect();
        return rect.top > viewportHeight && rect.height > 40 && Number(getComputedStyle(el).opacity) < 0.05;
      }).length;
      const reasons = [];
      if (libraries.length) reasons.push(`scroll libraries: ${libraries.join(', ')}`);
      if (pinned) reasons.push(`${pinned} pinned elements`);
      if (tallWithSticky.length) reasons.push(`${tallWithSticky.length} blocks taller than 3 screens with sticky/fixed content`);
      if (blocks.length && screenSized / blocks.length >= 0.3) reasons.push(`${screenSized}/${blocks.length} blocks are exactly one screen tall`);
      if (hiddenUntilScrolled > 20) reasons.push(`${hiddenUntilScrolled} below-the-fold elements are transparent until scrolled`);
      return {
        scrollDriven: reasons.length >= 2 ? 'likely' : reasons.length === 1 ? 'possible' : 'unlikely',
        reasons,
        tallWithSticky,
        pageHeight: document.scrollingElement.scrollHeight,
      };
    },

    // Scroll positions for frame-by-frame capture: each block's top, plus one frame per screen
    // inside blocks taller than 1.5 screens. Pass them to goTo() and take a viewport screenshot each.
    scrollFrames(selector) {
      const viewportHeight = window.innerHeight;
      const maxY = document.scrollingElement.scrollHeight - viewportHeight;
      const positions = [0];
      for (const block of topBlocks(selector)) {
        const top = Math.round(pageTop(block));
        positions.push(top);
        if (block.offsetHeight > viewportHeight * 1.5) {
          for (let y = top + viewportHeight * 2; y < top + block.offsetHeight - viewportHeight; y += viewportHeight * 2) positions.push(Math.round(y));
        }
      }
      const unique = [...new Set(positions.map(y => Math.min(Math.max(y, 0), maxY)))].sort((a, b) => a - b);
      const frames = unique.filter((y, index) => index === 0 || y - unique[index - 1] >= viewportHeight * 0.5);
      // Always end at the very bottom so the footer is fully captured, even if it overlaps the previous frame.
      if (frames[frames.length - 1] < maxY) frames.push(maxY);
      return frames;
    },

    async goTo(y, waitMs = 1000) {
      window.scrollTo(0, y);
      await sleep(waitMs);
      return Math.round(window.scrollY);
    },

    links() {
      const collect = selector => {
        const seen = new Set();
        return [...document.querySelectorAll(selector)]
          .filter(a => a.href && !seen.has(a.href) && seen.add(a.href))
          .map(a => ({ text: cleanText(a.innerText || a.getAttribute('aria-label'), 60), href: a.href, visible: isVisible(a) }));
      };
      // Prefer semantic markup, then class / id naming, then position (top of page / last block).
      let header = collect('header a[href], [role=banner] a[href], nav a[href]');
      let footer = collect('footer a[href], [role=contentinfo] a[href]');
      const source = { header: 'semantic', footer: 'semantic' };
      if (!header.length) {
        header = collect('[class*="header"] a[href], [id*="header"] a[href], [class*="nav"] a[href], [id*="nav"] a[href], [class*="menu"] a[href]')
          .filter(link => link.visible);
        source.header = 'class-name';
      }
      if (!header.length) {
        const seen = new Set();
        header = [...document.querySelectorAll('a[href]')]
          .filter(a => isVisible(a) && a.getBoundingClientRect().top + window.scrollY < 200 && !seen.has(a.href) && seen.add(a.href))
          .map(a => ({ text: cleanText(a.innerText || a.getAttribute('aria-label'), 60), href: a.href, visible: true }));
        source.header = 'position';
      }
      if (!footer.length) {
        footer = collect('[class*="footer"] a[href], [id*="footer"] a[href]');
        source.footer = 'class-name';
      }
      if (!footer.length) {
        const last = topBlocks().pop();
        footer = last ? [...last.querySelectorAll('a[href]')].map(a => ({ text: cleanText(a.innerText, 60), href: a.href, visible: isVisible(a) })) : [];
        source.footer = 'last-block';
      }
      const sameOrigin = [...document.querySelectorAll('a[href]')]
        .map(a => { try { return new URL(a.href); } catch { return null; } })
        .filter(url => url && url.origin === location.origin);
      const groups = tally();
      sameOrigin.forEach(url => groups.add('/' + url.pathname.split('/').filter(Boolean).slice(0, 2).join('/')));
      return {
        header,
        footer,
        source,
        pathGroups: groups.top(40),
        external: [...new Set([...document.querySelectorAll('a[href^="http"]')].map(a => { try { return new URL(a.href).host; } catch { return null; } }).filter(host => host && host !== location.host))],
      };
    },

    // Top-level layout blocks with measured heights. Pass a selector when the heuristic picks the wrong level.
    sections(selector) {
      return topBlocks(selector).map((el, index) => {
        const style = getComputedStyle(el);
        const heading = el.querySelector('h1, h2, h3');
        const inner = el.querySelector('[class*="container"], [class*="inner"]') || el;
        const innerStyle = getComputedStyle(inner);
        const columns = innerStyle.display.includes('grid')
          ? innerStyle.gridTemplateColumns.split(' ').length
          : [...inner.children].filter(child => isVisible(child) && Math.abs(child.getBoundingClientRect().top - inner.getBoundingClientRect().top) < 4).length;
        return {
          index: index + 1,
          ...describe(el),
          top: Math.round(pageTop(el)),
          height: Math.round(el.getBoundingClientRect().height),
          heading: heading ? cleanText(heading.innerText, 80) : undefined,
          background: toHex(style.backgroundColor) || (style.backgroundImage !== 'none' ? 'image' : undefined),
          padding: `${style.paddingTop} ${style.paddingBottom}`,
          columnsGuess: columns || undefined,
          images: el.querySelectorAll('img, picture, video, iframe').length,
          links: el.querySelectorAll('a[href]').length,
          buttons: el.querySelectorAll('button, .button, .btn, [class*="button"]').length,
          forms: el.querySelectorAll('form').length,
          text: cleanText(el.innerText, 120),
        };
      });
    },

    tokens({ limit = 4000 } = {}) {
      const colors = { text: tally(), background: tally(), border: tally() };
      const fonts = tally();
      const fontSizes = tally();
      const radius = tally();
      const shadows = tally();
      const gaps = tally();
      const paddings = tally();
      const maxWidths = tally();
      // Text styles grouped by visual signature, so the type scale reflects what is actually used
      // instead of whichever element happens to be the first <h1>.
      const textStyles = new Map();
      const elements = [...document.querySelectorAll('body *')].filter(el => isVisible(el) && isInViewportX(el)).slice(0, limit);
      for (const el of elements) {
        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        const ownText = [...el.childNodes].filter(node => node.nodeType === 3).map(node => node.textContent).join(' ').trim();
        if (ownText) {
          colors.text.add(toHex(style.color));
          fonts.add(style.fontFamily.split(',')[0].replace(/["']/g, '').trim());
          fontSizes.add(style.fontSize);
          const key = [style.fontFamily.split(',')[0].replace(/["']/g, '').trim(), style.fontSize, style.fontWeight, style.textTransform].join('|');
          const entry = textStyles.get(key) || {
            fontFamily: key.split('|')[0], fontSize: style.fontSize, fontWeight: style.fontWeight,
            lineHeight: style.lineHeight, letterSpacing: style.letterSpacing,
            textTransform: style.textTransform !== 'none' ? style.textTransform : undefined,
            color: toHex(style.color), tags: new Set(), count: 0, samples: [],
          };
          entry.count += 1;
          entry.tags.add(el.tagName.toLowerCase());
          if (entry.samples.length < 3 && ownText.length > 1) entry.samples.push(cleanText(ownText, 40));
          textStyles.set(key, entry);
        }
        colors.background.add(toHex(style.backgroundColor), Math.max(1, Math.round((rect.width * rect.height) / 10000)));
        if (parseFloat(style.borderTopWidth) > 0 && style.borderTopStyle !== 'none') colors.border.add(toHex(style.borderTopColor));
        if (style.borderRadius !== '0px') radius.add(style.borderRadius);
        if (style.boxShadow !== 'none') shadows.add(style.boxShadow);
        if (/flex|grid/.test(style.display) && style.gap !== 'normal' && style.gap !== '0px') gaps.add(style.gap);
        if (rect.width >= window.innerWidth * 0.9 && parseFloat(style.paddingTop) >= 24) paddings.add(`${style.paddingTop} / ${style.paddingBottom}`);
        if (style.maxWidth !== 'none' && rect.width >= 600) maxWidths.add(style.maxWidth);
      }
      const typeScale = [...textStyles.values()]
        .filter(entry => entry.samples.length)
        .sort((a, b) => parseFloat(b.fontSize) - parseFloat(a.fontSize) || b.count - a.count)
        .slice(0, 20)
        .map(entry => ({ ...entry, tags: [...entry.tags].slice(0, 5) }));

      // CSS custom properties and media query breakpoints from readable stylesheets.
      const cssVariables = new Map();
      const breakpoints = tally();
      const inaccessibleSheets = [];
      const walk = rules => {
        for (const rule of rules) {
          if (rule.media && rule.cssRules) {
            (rule.conditionText || rule.media.mediaText || '').match(/(min|max)-width:\s*[\d.]+px/g)?.forEach(bp => breakpoints.add(bp.replace(/\s+/g, '')));
            walk(rule.cssRules);
          } else if (rule.style && /:root|^html|^body|elementor-kit/.test(rule.selectorText || '')) {
            for (const name of rule.style) {
              if (name.startsWith('--') && !cssVariables.has(name)) cssVariables.set(name, rule.style.getPropertyValue(name).trim());
            }
          } else if (rule.cssRules) {
            walk(rule.cssRules);
          }
        }
      };
      for (const sheet of document.styleSheets) {
        try { walk(sheet.cssRules); } catch { inaccessibleSheets.push(sheet.href); }
      }
      const rootStyle = getComputedStyle(document.documentElement);
      const variables = [...cssVariables.entries()].slice(0, 300).map(([name, declared]) => ({
        name, declared, computed: rootStyle.getPropertyValue(name).trim() || undefined,
      }));

      // Distinct button / input looks, deduplicated by visual signature.
      const componentStyles = (selector, kind) => {
        const seen = new Map();
        for (const el of document.querySelectorAll(selector)) {
          if (!isVisible(el) || !isInViewportX(el)) continue;
          const style = getComputedStyle(el);
          const signature = [style.backgroundColor, style.color, style.borderRadius, style.borderTopWidth, style.borderTopColor, style.fontSize, style.fontWeight, style.paddingTop, style.paddingLeft, style.textTransform].join('|');
          if (seen.has(signature)) { seen.get(signature).count += 1; continue; }
          const rect = el.getBoundingClientRect();
          seen.set(signature, {
            kind,
            text: cleanText(el.innerText || el.value || el.placeholder, 40),
            count: 1,
            pageRect: [rect.x, rect.y + window.scrollY, rect.width, rect.height].map(Math.round),
            css: {
              background: toHex(style.backgroundColor) || style.backgroundImage.slice(0, 80),
              color: toHex(style.color),
              border: `${style.borderTopWidth} ${style.borderTopStyle} ${toHex(style.borderTopColor) || 'transparent'}`,
              borderRadius: style.borderRadius,
              padding: `${style.paddingTop} ${style.paddingRight} ${style.paddingBottom} ${style.paddingLeft}`,
              font: `${style.fontWeight} ${style.fontSize}/${style.lineHeight} ${style.fontFamily.split(',')[0]}`,
              textTransform: style.textTransform !== 'none' ? style.textTransform : undefined,
              boxShadow: style.boxShadow !== 'none' ? style.boxShadow : undefined,
            },
          });
        }
        return [...seen.values()].sort((a, b) => b.count - a.count).slice(0, 8);
      };

      const loadedFonts = [...document.fonts].filter(font => font.status === 'loaded')
        .map(font => `${font.family.replace(/["']/g, '')} ${font.weight} ${font.style}`);
      const fontSources = [...document.querySelectorAll('link[href]')].map(link => link.href)
        .filter(href => /fonts\.googleapis|use\.typekit|fonts\.bunny|font/i.test(href));

      return {
        url: location.href,
        viewport: window.innerWidth,
        colors: { text: colors.text.top(16), background: colors.background.top(16), border: colors.border.top(10) },
        fontFamilies: fonts.top(8),
        loadedFonts: [...new Set(loadedFonts)].slice(0, 30),
        fontSources,
        fontSizes: fontSizes.top(16),
        typeScale,
        radius: radius.top(10),
        shadows: shadows.top(8),
        gaps: gaps.top(10),
        sectionPaddings: paddings.top(10),
        maxWidths: maxWidths.top(8),
        breakpoints: breakpoints.top(16),
        cssVariables: variables,
        inaccessibleSheets: inaccessibleSheets.filter(Boolean),
        components: [
          ...componentStyles('button, input[type=submit], input[type=button], a.button, a.btn, .btn, [class*="button"]:not([class*="buttons"])', 'button'),
          ...componentStyles('input[type=text], input[type=email], input[type=tel], input[type=search], textarea, select', 'input'),
        ],
      };
    },
  };
  return 'window.__siteRef installed: prepare(opts), inspect(), scrollFrames(selector?), goTo(y), links(), sections(selector?), tokens()';
}
