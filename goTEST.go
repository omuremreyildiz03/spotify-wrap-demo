package main

import "fmt"

// Add two integers
func add(a int, b int) int {
    // Returns sum of a and b
    return a + b
}

func subtract(a int, b int) int {
    return a - b
}

func multiply(a int, b int) int {
    // Multiply two numbers
    return a * b
}

func factorial(n int) int {
    // Calculate factorial recursively
    if n <= 1 {
        return 1
    }
    return n * factorial(n-1)
}

func greet(name string) string {
    // Generate greeting
    return fmt.Sprintf("Hello, %s!", name)
}

func isPrime(n int) bool {
    if n < 2 {
        return false
    }
    for i := 2; i < n; i++ {
        if n%i == 0 {
            return false
        }
    }
    return true
}