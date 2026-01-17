/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

// ========== Child Component (TodoItem) ==========
export class TodoItem extends Component {
    static template = "counter.TodoItem";
    static props = {
        todo: Object,
        index: Number,
        itemColor: String,
        itemPriority: String,
        maxLength: Number,
        onToggle: Function,
        onDelete: Function,
    };

    setup() {
        console.log("📌 Item data:", {
            color: this.props.itemColor,
            priority: this.props.itemPriority,
            maxLength: this.props.maxLength
        });
    }

    get isTooLong() {
        return this.props.todo.title.length > this.props.maxLength;
    }

    toggleTodo() {
        this.props.onToggle(this.props.todo.id);
    }

    deleteTodo() {
        this.props.onDelete(this.props.todo.id);
    }
}

// ========== Parent Component (TodoEnv) ==========
export class TodoEnv extends Component {
    static template = "counter.TodoEnv";
    static components = { TodoItem };

    setup() {
        this.state = useState({
            todos: [
                { id: 1, title: "Learn OWL Environment", done: false, priority: "high" },
                { id: 2, title: "Pass data through props", done: false, priority: "medium" },
                { id: 3, title: "Understand data flow", done: false, priority: "low" },
            ],
            newTodo: "",
            theme: "light",
            maxTitleLength: 25,
        });

        console.log("🌍 App initialized with config:", {
            maxLength: this.state.maxTitleLength,
            theme: this.state.theme
        });
    }

    getColorByPriority(priority) {
        const colors = {
            high: "#ff6b6b",
            medium: "#ffd93d",
            low: "#6bcf7f"
        };
        return colors[priority] || "#95a5a6";
    }

    // ✅ Handle Enter key
    onKeyup(ev) {
        if (ev.key === 'Enter' || ev.keyCode === 13) {
            this.addTodo();
        }
    }

    addTodo() {
        if (this.state.newTodo.trim()) {
            const newId = Math.max(...this.state.todos.map(t => t.id), 0) + 1;
            this.state.todos.push({
                id: newId,
                title: this.state.newTodo,
                done: false,
                priority: "medium"
            });
            this.state.newTodo = "";
        }
    }

    toggleTodo(id) {
        const todo = this.state.todos.find(t => t.id === id);
        if (todo) {
            todo.done = !todo.done;
        }
    }

    deleteTodo(id) {
        const index = this.state.todos.findIndex(t => t.id === id);
        if (index > -1) {
            this.state.todos.splice(index, 1);
        }
    }

    changePriority(id, priority) {
        const todo = this.state.todos.find(t => t.id === id);
        if (todo) {
            todo.priority = priority;
        }
    }

    changeTheme() {
        this.state.theme = this.state.theme === "light" ? "dark" : "light";
    }

    get completedCount() {
        return this.state.todos.filter(t => t.done).length;
    }

    get pendingCount() {
        return this.state.todos.filter(t => !t.done).length;
    }
}

registry.category("actions").add("todo_env.action", TodoEnv);