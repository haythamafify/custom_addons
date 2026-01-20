const { Component, mount, useState, xml } = owl;

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
                       placeholder="Add your new task" t-model="state.name"/>

                <input type="color"
                       class="form-control-lg form-control border-0 m-0" t-model="state.color"/>

             <button type="button" class="btn btn-primary" t-on-click="add_task">
    Submit
</button>
            </div>

            <ul class="d-flex flex-column mt-5 p-0">
                <li class="d-flex justify-content-between align-items-center p-3 border mb-3 rounded-3">

                    <div class="form-check form-switch fs-5">
                        <input class="form-check-input"
                               type="checkbox"
                               id="checkDefault"/>
                        <label class="form-check-label" for="checkDefault">
                            Default checkbox
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
            </ul>

        </div>
    </div>
</div>


  <ul class="d-flex flex-column mt-0 p-0">
    <t t-foreach="tasks" t-as="task" t-key="task.id">
 <li  t-att-style="'background-color: ' + task.color" class="d-flex justify-content-between align-items-center p-3 border mb-3 rounded-3" >

                    <div class="form-check form-switch fs-5">
                        <input class="form-check-input"
                               type="checkbox"
                               t-att-id="task.id"/>
                        <label class="form-check-label" t-att-for="task.id">
                           <t t-esc="task.name"/>
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
    </t>
  </ul>

`;

  setup() {
    this.state = useState({
      name: "",
      color: "#00C897",
      isCompleted: false,
    });
    this.tasks = useState([
      { id: 1, name: "Task 1", color: "#FF0220", isCompleted: false },
      { id: 2, name: "Task 2", color: "#00C897", isCompleted: true },
      { id: 3, name: "Task 3", color: "#3B82F6", isCompleted: false },
    ]);
  }

  add_task() {
    console.log("inside add task");

    console.log(this.state);
    
  }
}

mount(Root, document.getElementById("Root"));
