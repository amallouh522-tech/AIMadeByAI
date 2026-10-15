const API_BASE_URL = "https://jsonplaceholder.typicode.com";

async function requestJson(url, options = {}) {
  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
  } catch (error) {
    throw new Error(`Network request failed: ${error.message}`, { cause: error });
  }

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof payload === "string" ? payload : JSON.stringify(payload);
    throw new Error(`HTTP ${response.status}: ${detail}`);
  }
  return payload;
}

async function loadPosts(limit = 8) {
  if (!Number.isInteger(limit) || limit < 1 || limit > 100) {
    throw new RangeError("limit must be an integer between 1 and 100");
  }
  const posts = await requestJson(`${API_BASE_URL}/posts?_limit=${limit}`);
  if (!Array.isArray(posts)) {
    throw new TypeError("The posts endpoint did not return an array");
  }
  return posts.map(({ id, title, body }) => ({ id, title, body }));
}

class Store {
  #state;
  #listeners = new Set();

  constructor(initialState) {
    if (initialState === null || typeof initialState !== "object") {
      throw new TypeError("Initial state must be an object");
    }
    this.#state = structuredClone(initialState);
  }

  getState() {
    return structuredClone(this.#state);
  }

  update(updater) {
    if (typeof updater !== "function") {
      throw new TypeError("Updater must be a function");
    }
    const nextState = updater(this.getState());
    if (nextState === null || typeof nextState !== "object") {
      throw new TypeError("Updater must return an object");
    }
    this.#state = structuredClone(nextState);
    for (const listener of this.#listeners) {
      listener(this.getState());
    }
  }

  subscribe(listener) {
    if (typeof listener !== "function") {
      throw new TypeError("Listener must be a function");
    }
    this.#listeners.add(listener);
    listener(this.getState());
    return () => this.#listeners.delete(listener);
  }
}

const taskStore = new Store({ tasks: [], filter: "all", loading: false, error: "" });

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function selectVisibleTasks(state) {
  if (state.filter === "active") return state.tasks.filter((task) => !task.completed);
  if (state.filter === "completed") return state.tasks.filter((task) => task.completed);
  return state.tasks;
}

function renderTasks(root, state) {
  const tasks = selectVisibleTasks(state);
  const list = root.querySelector("[data-task-list]");
  const status = root.querySelector("[data-status]");
  list.replaceChildren();

  for (const task of tasks) {
    const item = document.createElement("li");
    item.className = "flex items-center gap-3 border-b border-slate-200 py-3";
    item.innerHTML = `
      <input type="checkbox" data-toggle="${task.id}" ${task.completed ? "checked" : ""}>
      <span class="flex-1 ${task.completed ? "line-through text-slate-400" : "text-slate-800"}">${escapeHtml(task.title)}</span>
      <button type="button" data-remove="${task.id}" aria-label="Delete ${escapeHtml(task.title)}">Delete</button>
    `;
    list.append(item);
  }

  status.textContent = state.error || (state.loading ? "Loading tasks..." : `${tasks.length} tasks`);
}

function mountTaskApp(root) {
  const unsubscribe = taskStore.subscribe((state) => renderTasks(root, state));
  const form = root.querySelector("[data-task-form]");

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const input = form.elements.namedItem("title");
    const title = input.value.trim();
    if (!title) {
      input.setCustomValidity("Enter a task title.");
      input.reportValidity();
      return;
    }
    input.setCustomValidity("");
    taskStore.update((state) => ({
      ...state,
      error: "",
      tasks: [...state.tasks, { id: crypto.randomUUID(), title, completed: false }],
    }));
    form.reset();
  });

  root.addEventListener("change", (event) => {
    const taskId = event.target.dataset.toggle;
    if (!taskId) return;
    taskStore.update((state) => ({
      ...state,
      tasks: state.tasks.map((task) => task.id === taskId
        ? { ...task, completed: event.target.checked }
        : task),
    }));
  });

  root.addEventListener("click", (event) => {
    const removeId = event.target.dataset.remove;
    if (removeId) {
      taskStore.update((state) => ({
        ...state,
        tasks: state.tasks.filter((task) => task.id !== removeId),
      }));
    }
    const filter = event.target.dataset.filter;
    if (["all", "active", "completed"].includes(filter)) {
      taskStore.update((state) => ({ ...state, filter }));
    }
  });

  return unsubscribe;
}

function summarizePosts(posts) {
  return posts
    .filter((post) => post.title.length >= 12)
    .map((post) => ({ id: post.id, title: post.title.trim(), wordCount: post.body.split(/\s+/).length }))
    .reduce((summary, post) => {
      summary.totalPosts += 1;
      summary.totalWords += post.wordCount;
      summary.longestTitle = post.title.length > summary.longestTitle.length
        ? post.title
        : summary.longestTitle;
      return summary;
    }, { totalPosts: 0, totalWords: 0, longestTitle: "" });
}

async function startPostExample(output) {
  output.textContent = "Loading posts...";
  try {
    const posts = await loadPosts(10);
    const summary = summarizePosts(posts);
    output.textContent = JSON.stringify(summary, null, 2);
  } catch (error) {
    output.textContent = `Could not load posts: ${error.message}`;
  }
}

export {
  Store,
  escapeHtml,
  loadPosts,
  mountTaskApp,
  requestJson,
  startPostExample,
  summarizePosts,
  taskStore,
};