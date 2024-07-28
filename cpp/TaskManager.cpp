#include "TaskManager.h"
#include <iostream>
#include <fstream>

TaskManager::TaskManager() {}

void TaskManager::addTask(const std::string& description) {
    Task task(description);
    tasks.push_back(task);
}

void TaskManager::completeTask(int index) {
    if (index > 0 && index <= tasks.size()) {
        tasks[index - 1].setCompleted(true);
    }
}

void TaskManager::listTasks(std::ostream& os) const {
    for (size_t i = 0; i < tasks.size(); ++i) {
        os << (i + 1) << ". [" << (tasks[i].isCompleted() ? "x" : " ") << "] " << tasks[i].getDescription() << "\n";
    }
}

void TaskManager::saveTasks(const std::string& filename) const {
    std::ofstream outFile(filename);
    for (const auto& task : tasks) {
        outFile << task.getDescription() << "|" << task.isCompleted() << "\n";
    }
}

void TaskManager::loadTasks(const std::string& filename) {
    std::ifstream inFile(filename);
    if (inFile) {
        tasks.clear();
        std::string line;
        while (std::getline(inFile, line)) {
            size_t delimiterPos = line.find('|');
            std::string description = line.substr(0, delimiterPos);
            bool completed = line.substr(delimiterPos + 1) == "1";
            Task task(description, completed);
            tasks.push_back(task);
        }
    }
}

const std::vector<Task>& TaskManager::getTasks() const {
    return tasks;
}
