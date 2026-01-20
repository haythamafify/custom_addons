const { Component, mount, useState, xml } = owl;

class Task extends Component {
  static template = xml`
    <li t-att-style="'background-color: ' + props.task.color" 
        class="d-flex justify-content-between align-items-center p-3 border mb-3 rounded-3">

      <div class="form-check form-switch fs-5">
        <input class="form-check-input"
               type="checkbox" 
               t-on-click="() => props.onToggle(props.task.id)"
               t-att-checked="props.task.isCompleted"
               t-att-id="props.task.id"/>
        <label class="form-check-label" 
               t-att-for="props.task.id"
               t-attf-class="{{props.task.isCompleted ? 'text-decoration-line-through' : ''}}">
          <t t-esc="props.task.name"/>
        </label>
      </div>

      <div>
        <button class="btn btn-primary me-2">
          <i class="bi bi-pencil"></i>
        </button>

        <button class="btn btn-danger">
          <i class="bi bi-trash"></i>
        </button>
      </div>
    </li>
  `;

  static props = ["task", "onToggle"];
}

class Root extends Component {
  static template = xml`
    <div class="container mt-5">
      <div class="row my-5 py-5">
        <div class="col-lg-6 offset-lg-3">
          <h1 class="text-center mb-4 fw-bold main_title">Todo List OWL</h1>
          <p class="text-center h5 text-muted mb-5">OWL Tutorial for Beginners</p>

          <div class="input-group w-100 d-flex p-2 border mb-3 align-items-center rounded-3">
            <input type="text"
                   class="form-control-lg flex-fill border-0"
                   placeholder="Add your new task" 
                   t-model="state.name"/>

            <input type="color"
                   class="form-control-lg form-control border-0 m-0" 
                   t-model="state.color"/>

            <button type="button" 
                    class="btn btn-primary" 
                    t-on-click="add_task">
              ADD TASK
            </button>
          </div>

          <ul class="d-flex flex-column mt-5 p-0">
            <t t-foreach="tasks" t-as="task" t-key="task.id">
              <Task task="task" onToggle.bind="toggleTask"/>
            </t>
          </ul>
        </div>
      </div>
    </div>
  `;

  static components = { Task };

  setup() {
    this.state = useState({
      name: "",
      color: "#00C897",
      isCompleted: false,
    });

    this.tasks = useState([]);
  }

  add_task() {
    if (!this.state.name.trim()) {
      alert("Please enter the task name");
      return;
    }

    const newTask = {
      id: this.tasks.length + 1,
      name: this.state.name,
      color: this.state.color,
      isCompleted: false,
    };

    this.tasks.push(newTask);

    this.state.name = "";
    this.state.color = "#00C897";
  }

  toggleTask(taskId) {
    const task = this.tasks.find(t => t.id === taskId);
    if (task) {
      task.isCompleted = !task.isCompleted;
    }
  }
}

mount(Root, document.getElementById("Root"));
