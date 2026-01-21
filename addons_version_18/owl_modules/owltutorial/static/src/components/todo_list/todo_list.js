/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class TodoList extends Component {
    static template = "owl.TodoList";
    
    setup() {
        this.state = useState({
            tasks: [
                { id: 1, text: "Learn OWL basics", completed: false },
                { id: 2, text: "Build Todo app", completed: false }
            ],
            newTaskText: ""
        });
    }
    
    onKeyup(event) {
        if (event.key === "Enter") {
            this.addTask();
        }
    }
    
    addTask() {
        if (this.state.newTaskText.trim()) {
            const newTask = {
                id: Date.now(),
                text: this.state.newTaskText,
                completed: false
            };
            this.state.tasks.push(newTask);
            this.state.newTaskText = "";
        }
    }
    
    toggleTask(taskId) {
        const task = this.state.tasks.find(t => t.id === taskId);
        if (task) {
            task.completed = !task.completed;
        }
    }
    
    deleteTask(taskId) {
        const index = this.state.tasks.findIndex(t => t.id === taskId);
        if (index !== -1) {
            this.state.tasks.splice(index, 1);
        }
    }
}

registry.category("actions").add("owl.todo_list_action", TodoList);
