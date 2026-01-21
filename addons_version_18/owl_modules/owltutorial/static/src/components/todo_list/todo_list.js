/** @odoo-module **/

import { Component, useState, onWillStart, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class TodoList extends Component {
    static template = "owl.TodoList";
    
    setup() {
        this.state = useState({
            taskList: [],  // Changed from 'tasks' to 'taskList'
            task: {        // Added task object for modal
                id: false,
                name: "",
                color: "#000000",
                completed: false
            },
            isEdit: false,
        });
        
        this.orm = useService("orm");
        this.model = "owl.todo.list";
        this.searchInput = useRef("search-input");
        
        onWillStart(async () => {
            await this.getAllTasks();
        });
    }
    
    async getAllTasks() {
        this.state.taskList = await this.orm.searchRead(
            this.model,
            [],
            ["name", "completed", "color"]
        );
    }
    
    addTask() {
        this.state.isEdit = false;
        this.state.task = {
            id: false,
            name: "",
            color: "#000000",
            completed: false
        };
    }
    
    async saveTask() {
        if (this.state.task.name.trim()) {
            if (this.state.isEdit) {
                await this.orm.write(this.model, [this.state.task.id], {
                    name: this.state.task.name,
                    color: this.state.task.color,
                    completed: this.state.task.completed
                });
            } else {
                await this.orm.create(this.model, [{
                    name: this.state.task.name,
                    color: this.state.task.color,
                    completed: this.state.task.completed
                }]);
            }
            
            await this.getAllTasks();
            // Close modal programmatically
            document.querySelector('#exampleModal .btn-close').click();
        }
    }
    
    editTask(task) {
        this.state.isEdit = true;
        this.state.task = {
            id: task.id,
            name: task.name,
            color: task.color,
            completed: task.completed
        };
    }
    
    async toggleTask(event, task) {
        await this.orm.write(this.model, [task.id], {
            completed: !task.completed
        });
        await this.getAllTasks();
    }
    
    async updateColor(event, task) {
        await this.orm.write(this.model, [task.id], {
            color: event.target.value
        });
        await this.getAllTasks();
    }
    
    async deleteTask(task) {
        await this.orm.unlink(this.model, [task.id]);
        await this.getAllTasks();
    }
    
    async searchTasks() {
        const text = this.searchInput.el.value;
        if (text.trim()) {
            this.state.taskList = await this.orm.searchRead(
                this.model,
                [["name", "ilike", text]],
                ["name", "completed", "color"]
            );
        } else {
            await this.getAllTasks();
        }
    }
}

registry.category("actions").add("owl.todo_list_action", TodoList);
