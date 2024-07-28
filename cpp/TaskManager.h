#ifndef TASKMANAGER_H
#define TASKMANAGER_H

#include <vector>
#include <string>
#include "Task.h"
#include <ostream>

class TaskManager {
public:
    TaskManager();
    void addTask(const std::string& description);
    void completeTask(int index);
    void listTasks(std::ostream& os) const;
    void saveTasks(const std::string& filename) const;
    void loadTasks(const std::string& filename);

    const std::vector<Task>& getTasks() const;

private:
    std::vector<Task> tasks;
};

#endif
