#pragma once
#include <string>

class Vehicle {
public:
    std::string brand;
    int year;

    Vehicle(std::string brand, int year);
    std::string getBrand();
    int getYear();
    void honk();
};

class Car : public Vehicle {
public:
    int numDoors;

    Car(std::string brand, int year, int numDoors);
    void drive();
    void park();
};