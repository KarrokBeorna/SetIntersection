cmake_minimum_required(VERSION 3.25)
project(SetIntersection)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_FLAGS -fopenmp)

add_executable(SetIntersection main.cpp)
