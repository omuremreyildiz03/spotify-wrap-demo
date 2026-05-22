#pragma once
#include <string>
#include <iostream>

class Vehicle {
public:
    std::string brand;
    int year;

    Vehicle(std::string brand, int year) {
        // Initialize vehicle
        this->brand = brand;
        this->year = year;
    }

    std::string getBrand() {
        // Return brand name
        return this->brand;
    }

    int getYear() {
        return this->year;
    }

    void honk() {
        // Make honk sound
        std::cout << "Beep beep!" << std::endl;
    }
};

class Car : public Vehicle {
public:
    int numDoors;

    Car(std::string brand, int year, int numDoors) : Vehicle(brand, year) {
        // Initialize car with door count
        this->numDoors = numDoors;
    }

    void drive() {
        // Start driving
        std::cout << brand << " is driving." << std::endl;
    }

    void park() {
        std::cout << brand << " is parked." << std::endl;
    }
};