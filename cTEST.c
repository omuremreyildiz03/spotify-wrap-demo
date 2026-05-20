#include <stdio.h>
#include <stdlib.h>

// Calculate area of rectangle
int calculateArea(int width, int height) {
    // Multiply width by height
    return width * height;
}

int calculatePerimeter(int width, int height) {
    // Sum all sides
    return 2 * (width + height);
}

float calculateCircleArea(float radius) {
    // Pi times radius squared
    return 3.14159 * radius * radius;
}

int findMax(int a, int b) {
    if (a > b) return a;
    return b;
}

int factorial(int n) {
    // Recursive factorial
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}