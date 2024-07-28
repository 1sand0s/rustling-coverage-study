// main.cpp

#include <iostream>
#include "TaskManager.h"

void displayMenu() {
    std::cout << "\nTo-Do List:\n";
    std::cout << "1. Add task\n";
    std::cout << "2. Complete task\n";
    std::cout << "3. List tasks\n";
    std::cout << "4. Save tasks\n";
    std::cout << "5. Load tasks\n";
    std::cout << "6. Exit\n";
    std::cout << "Enter your choice: ";
}

int handleUserInput() {
    int choice;
    std::cin >> choice;
    return choice;
}

int main() {
    TaskManager taskManager;

    while (true) {
        displayMenu();
        int choice = handleUserInput();

        switch (choice) {
            case 1:
                taskManager.addTask();
                break;
            case 2:
                taskManager.completeTask();
                break;
            case 3:
                taskManager.listTasks();
                break;
            case 4:
                taskManager.saveTasks();
                std::cout << "Tasks saved.\n";
                break;
            case 5:
                taskManager.loadTasks();
                std::cout << "Tasks loaded.\n";
                break;
            case 6:
                std::cout << "Exiting...\n";
                return 0;
            default:
                std::cout << "Invalid choice! Please try again.\n";
                break;
        }
    }
}
