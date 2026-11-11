# 前端框架審閱規則（Frontend Framework Patterns）

> 本檔自 `agents/frontend-code-reviewer.md` 抽離，收錄 Vue 3 / Vue 2 / Nuxt 2 的框架專屬審閱規則。
> 審閱變更含 Vue / Nuxt 程式碼時，`frontend-code-reviewer` agent 會在執行階段讀取本檔並套用。

## Vue 3 Patterns (HIGH)

審閱 Vue 3 / Composition API 程式碼時，額外檢查：

- **Props 變動（Props mutation）** — 直接改 props，而非 emit 事件
- **`v-for` 缺少 `key`** — 項目會重排時用陣列 index 當 key
- **`computed` 內有副作用** — `computed` 必須是純函式；副作用應放在 `watch`
- **`watch` 缺少清理** — `watchEffect`/`watch` 內的非同步操作或計時器沒有透過 `onCleanup` 清理
- **記憶體洩漏（Memory leaks）** — 事件監聽或計時器註冊後未在 `onUnmounted` 移除
- **解構導致失去 reactivity** — 解構 `reactive()` 物件卻沒用 `toRefs()`
- **Prop drilling** — props 穿透 3 層以上（改用 `provide`/`inject` 或 Pinia）
- **缺少 loading/error 狀態** — 非同步取資料時沒有 fallback UI
- **`ref` 與 `reactive` 用法不當** — 對基本型別用 `reactive()`，或對大型巢狀物件不必要地用 `ref()`
- **`defineProps` / `defineEmits` 未加型別** — props 與 emits 定義缺少 TypeScript 泛型
- **`defineExpose` 過度暴露** — 暴露了應保持私有的內部狀態/方法
```vue
<!-- BAD: Mutating props directly -->
<script setup lang="ts">
const props = defineProps<{ modelValue: string }>();
props.modelValue = 'new value'; // Direct mutation!
</script>

<!-- GOOD: Emit to parent -->
<script setup lang="ts">
const props = defineProps<{ modelValue: string }>();
const emit = defineEmits<{ 'update:modelValue': [value: string] }>();
emit('update:modelValue', 'new value');
</script>
```
```vue
<!-- BAD: Index as key on reorderable list -->
<li v-for="(item, i) in items" :key="i">{{ item.name }}</li>

<!-- GOOD: Stable unique key -->
<li v-for="item in items" :key="item.id">{{ item.name }}</li>
```
```typescript
// BAD: Side effect inside computed
const fullName = computed(() => {
  document.title = `${firstName.value} ${lastName.value}`; // Side effect!
  return `${firstName.value} ${lastName.value}`;
});

// GOOD: Pure computed + separate watch
const fullName = computed(() => `${firstName.value} ${lastName.value}`);
watch(fullName, (name) => { document.title = name; });
```
```typescript
// BAD: Missing cleanup in watchEffect
watchEffect(() => {
  const timer = setInterval(() => fetchData(), 3000);
  // timer never cleared!
});

// GOOD: Cleanup via onCleanup
watchEffect((onCleanup) => {
  const timer = setInterval(() => fetchData(), 3000);
  onCleanup(() => clearInterval(timer));
});
```
```typescript
// BAD: Reactivity lost after destructuring reactive()
const state = reactive({ count: 0, name: 'Danny' });
const { count, name } = state; // count and name are no longer reactive!

// GOOD: Use toRefs to preserve reactivity
const state = reactive({ count: 0, name: 'Danny' });
const { count, name } = toRefs(state);
```
```typescript
// BAD: Untyped props and emits
const props = defineProps(['title', 'count']);
const emit = defineEmits(['update', 'close']);

// GOOD: Fully typed with TypeScript generics
const props = defineProps<{
  title: string;
  count: number;
}>();

const emit = defineEmits<{
  update: [value: number];
  close: [];
}>();
```
```typescript
// BAD: Memory leak — listener never removed
onMounted(() => {
  window.addEventListener('resize', handleResize);
});

// GOOD: Clean up in onUnmounted
onMounted(() => {
  window.addEventListener('resize', handleResize);
});
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
```

## Vue 2 Patterns (HIGH)

審閱 Vue 2 / Options API 程式碼時，額外檢查：

- **Reactivity 限制——新增屬性** — 未在 `data()` 宣告的屬性不具 reactivity；動態新增要用 `Vue.set()`
- **Reactivity 限制——陣列變動** — 直接索引賦值（`arr[0] = x`）與 `arr.length = n` 不具 reactivity；用陣列變動方法或 `Vue.set()`
- **Options API 中使用箭頭函式** — 生命週期 hook 或 methods 用箭頭函式會導致 `this` 為 undefined
- **`beforeDestroy` 缺少清理** — 事件監聽、計時器或第三方實例未在 `beforeDestroy` 釋放，造成記憶體洩漏
- **Props 變動（Props mutation）** — 直接改 props，而非 emit 事件
- **`v-for` 缺少 `key`** — 項目會重排時用陣列 index 當 key
- **`computed` 內有副作用** — `computed` 必須是純函式；副作用應放在 `watch`
- **`watch` 缺少 `immediate` / `deep`** — 監聽巢狀物件未加 `deep: true` 不會觸發
```javascript
// BAD: New property added after init — not reactive
this.user.age = 25;

// GOOD: Use Vue.set
this.$set(this.user, 'age', 25);
// or: Vue.set(this.user, 'age', 25);
```
```javascript
// BAD: Array index mutation — not reactive
this.items[0] = newItem;
this.items.length = 2;

// GOOD: Use mutation methods or Vue.set
this.$set(this.items, 0, newItem);
this.items.splice(2);
```
```javascript
// BAD: Arrow function — `this` is not the Vue instance
export default {
  created: () => {
    this.fetchData(); // `this` is undefined!
  }
}

// GOOD: Regular function
export default {
  created() {
    this.fetchData();
  }
}
```
```javascript
// BAD: Memory leak — third-party instance never destroyed
mounted() {
  this.chart = new Chart(this.$refs.canvas, options);
}

// GOOD: Clean up in beforeDestroy
mounted() {
  this.chart = new Chart(this.$refs.canvas, options);
},
beforeDestroy() {
  this.chart.destroy();
}
```
```javascript
// BAD: Deep watch missing
watch: {
  userProfile(newVal) { /* won't trigger on nested changes */ }
}

// GOOD: Enable deep
watch: {
  userProfile: {
    handler(newVal) { /* ... */ },
    deep: true,
    immediate: true
  }
}
```

## Nuxt 2 Patterns (HIGH)

審閱 Nuxt 2 程式碼時，額外檢查：

- **在 server 端存取 `window`/`document`** — Nuxt 2 的 `asyncData` 與 plugins 在 server 與 client 都會跑；瀏覽器全域物件須加防護
- **在非 page 元件用 `asyncData`** — `asyncData` 只在 page 層級元件可用；子元件改用 `fetch`
- **未處理的 `asyncData` 錯誤** — `asyncData` 中未處理的 rejection 會造成整頁錯誤；務必用 try/catch 包起來
- **`fetch` hook 缺少 error/loading 狀態** — `fetch`（Nuxt 2.12+）提供 `$fetchState`；忽略它就沒有 loading 或 error UI
- **在 `asyncData` 中存取 `this`** — `asyncData` 在元件實例化前執行，`this` 不可用，資料須以物件回傳
- **client-only 函式庫未加防護** — 依賴瀏覽器 API 的函式庫在頂層 import 會在 SSR 時崩潰
```javascript
// BAD: Accessing window on server — crashes SSR
export default {
  asyncData() {
    const width = window.innerWidth; // ReferenceError on server!
  }
}

// GOOD: Guard with process.client, or use mounted() for browser APIs
export default {
  asyncData() {
    if (process.client) {
      const width = window.innerWidth;
    }
  },
  mounted() {
    // Safe: mounted() only runs on client
    const width = window.innerWidth;
  }
}
```
```javascript
// BAD: asyncData in a child component — silently ignored
export default {
  asyncData() {
    return { posts: [] };
  }
}

// GOOD: Use fetch hook for child components
export default {
  data() {
    return { posts: [] };
  },
  async fetch() {
    this.posts = await this.$axios.$get('/api/posts');
  }
}
```
```javascript
// BAD: No error handling in asyncData — unhandled rejection = page crash
export default {
  async asyncData({ $axios }) {
    const data = await $axios.$get('/api/posts');
    return { data };
  }
}

// GOOD: Wrap in try/catch
export default {
  async asyncData({ $axios, error }) {
    try {
      const data = await $axios.$get('/api/posts');
      return { data };
    } catch (e) {
      error({ statusCode: 500, message: 'Failed to load data' });
    }
  }
}
```
```vue
<!-- BAD: fetch without loading/error state -->
<template>
  <ul>
    <li v-for="post in posts" :key="post.id">{{ post.title }}</li>
  </ul>
</template>

<!-- GOOD: Handle $fetchState -->
<template>
  <div>
    <p v-if="$fetchState.pending">Loading...</p>
    <p v-else-if="$fetchState.error">Error loading posts.</p>
    <ul v-else>
      <li v-for="post in posts" :key="post.id">{{ post.title }}</li>
    </ul>
  </div>
</template>
```
```javascript
// BAD: Client-only library imported at top level — crashes on server
import Swiper from 'swiper';

// GOOD: Dynamic import inside mounted()
mounted() {
  import('swiper').then(({ default: Swiper }) => {
    this.swiper = new Swiper(this.$refs.container, options);
  });
}
```
