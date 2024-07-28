// Task.cpp

#include "Task.h"

Task::Task(const std::string& description, bool completed)
    : description(description), completed(completed) {}

const std::string& Task::getDescription() const {
    return description;
}

bool Task::isCompleted() const {
    return completed;
}

void Task::setCompleted(bool completed) {
    this->completed = completed;
}
