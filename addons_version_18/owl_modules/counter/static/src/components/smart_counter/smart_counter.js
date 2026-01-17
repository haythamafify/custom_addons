/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";

export class SmartCounter extends Component {
    static template = "counter.SmartCounter";
    static props = {
        onTimeExceeded: { type: Function, optional: true }
    };

    setup() {
        this.state = useState({
            counter: 0,
            timer: 0
        });

        this.interval = null;

        onMounted(() => {
            this.startTimer();
        });

        onWillUnmount(() => {
            this.stopTimer();
        });
    }

    startTimer() {
        if (!this.interval) {
            this.interval = setInterval(() => {
                this.state.timer++;

                // Trigger callback when exceeding 60 seconds
                if (this.state.timer === 61 && this.props.onTimeExceeded) {
                    this.props.onTimeExceeded();
                }
            }, 1000);
        }
    }

    stopTimer() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    resetTimer() {
        this.stopTimer();
        this.state.timer = 0;
        this.startTimer();
    }

    increment() {
        this.state.counter++;
    }

    decrement() {
        this.state.counter--;
    }

    reset() {
        this.state.counter = 0;
        this.resetTimer();
    }

    get faceIcon() {
        return this.state.timer > 60 ? "😠" : "😊";
    }

    get timerColor() {
        if (this.state.timer > 60) return "text-danger";
        if (this.state.timer > 45) return "text-warning";
        return "text-success";
    }

    get formattedTimer() {
        const minutes = Math.floor(this.state.timer / 60);
        const seconds = this.state.timer % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}