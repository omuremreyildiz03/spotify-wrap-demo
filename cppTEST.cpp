#include <iostream>
#include <string>
#include <vector>

// Utility function
int add(int a, int b) {
    // Add two numbers
    return a + b;
}

class Animal {
public:
    std::string name;
    int age;

    Animal(std::string name, int age) {
        // Initialize animal
        this->name = name;
        this->age = age;
    }

    std::string getName() {
        return this->name;
    }

    int getAge() {
        return this->age;
    }

    void speak() {
        // Generic animal sound
        std::cout << "..." << std::endl;
    }
};

class Dog : public Animal {
public:
    Dog(std::string name, int age) : Animal(name, age) {}

    void speak() {
        // Dog specific sound
        std::cout << "Woof!" << std::endl;
    }

    void fetch(std::string item) {
        std::cout << name << " fetches " << item << std::endl;
    }
};