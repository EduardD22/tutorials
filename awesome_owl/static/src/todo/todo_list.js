import { Component, useState } from "@odoo/owl";
import { TodoItem } from "./todo_item";
import { useAutofocus } from "../utils";

export class TodoList extends Component {
    static template = "awesome_owl.todolist";
    static components = { TodoItem };

    setup() {
        this.ID = 1;
        this.todos = useState([]);
        useAutofocus("input");
       /* this.todos = useState([{ id: 3, description: "buy milk", isCompleted: true },]); */
    }

    addTodo(ev) {
        if (ev.keyCode === 13 && ev.target.value !== "") {
            this.todos.push({
                id: this.ID++,
                description: ev.target.value,
                isCompleted: false
            });
            ev.target.value = "";
        }
    }

    onChange(todoId) {
        const todo = this.todos.find((todo) => todo.id === todoId);
        if (todo) {
            todo.isCompleted = !todo.isCompleted;
        }
    }

    removeTodo(todoId) {
        const index = this.todos.findIndex((todo) => todo.id === todoId);
        if (index >= 0) {
           this.todos.splice(index, 1);
        }
    }

}