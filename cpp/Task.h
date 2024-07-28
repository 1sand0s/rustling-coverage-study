// Task.h

#ifndef TASK_H
#define TASK_H

#include <string>

class Task {
public:
    Task(const std::string& description, bool completed = false);

    const std::string& getDescription() const;
    bool isCompleted() const;
    void setCompleted(bool completed);
    
private:
    std::string description;
    bool completed;
};

#endif
