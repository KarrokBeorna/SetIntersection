#include <iostream>
#include <pthread.h>
#include <set>
#include <fstream>
#include <random>
#include <chrono>
#include <omp.h>

using namespace std;
using namespace std::chrono;

set<int> sh;
pthread_mutex_t mutex;

struct ThreadArgs {
    int start{}, end{};
    vector<int> set1Array;
    set<int>* set2;
    set<int>* set3;
};

set<int> generateSet(int size) {
    set<int> s;
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dis(1, size * 3);
    while (s.size() < size) {
        s.insert(dis(gen));
    }
    return s;
}

set<int> intersection_serial(const set<int>& set1, const set<int>& set2, const set<int>& set3) {
    set<int> intersectionSet;
    for (int a : set1) {
        if (set2.find(a) != set2.end() &&
            set3.find(a) != set3.end()) {
            intersectionSet.insert(a);
        }
    }
    return intersectionSet;
}

void* intersection_pthreads(void* arg) {
    auto* args = static_cast<ThreadArgs*>(arg);
    int start = args->start, end = args->end;
    set<int> result;
    for (int i = start; i < end; i++) {
        int a = args->set1Array[i];
        if (args->set2->find(a) != args->set2->end() &&
            args->set3->find(a) != args->set3->end()) {
            result.insert(a);
        }
    }

    pthread_mutex_lock(&mutex);
    for (int x : result) {
        sh.insert(x);
    }
    pthread_mutex_unlock(&mutex);

    return nullptr;
}

vector<int> intersection_openmp(const int NUM_THREADS,
                                const int arraySize,
                                const vector<int>& set1Array,
                                const set<int>& set2,
                                const set<int>& set3,
                                vector<int> result) {
    omp_set_num_threads(NUM_THREADS);
#pragma omp parallel for schedule(static) shared(arraySize, set1Array, set2, set3, result) default(none)
    for (int i = 0; i < arraySize; i++) {
        int a = set1Array[i];
        if (set2.find(a) != set2.end() &&
            set3.find(a) != set3.end()) {
            result[i] = a;
        }
    }
    return result;
}

int main() {

    ofstream ofs("executionTime.txt");
    vector<int> sizes = {10, 100, 1000, 10000, 50000, 100000, 500000, 1000000, 5000000, 10000000};
    vector<int> VECTOR_THREADS = {1, 2, 4, 6, 8, 12, 16};
    int numberOfLaunches = 10;

    for (int size : sizes) {
        set<int> Set1 = generateSet(size),
                 Set2 = generateSet(size),
                 Set3 = generateSet(size);

        if (Set1.size() > Set2.size()) {
            swap(Set1, Set2);
        }
        if (Set2.size() > Set3.size()) {
            swap(Set2, Set3);
        }
        if (Set1.size() > Set2.size()) {
            swap(Set1, Set2);
        }

        float setSize1 = Set1.size();
        float setSize2 = Set2.size();
        float setSize3 = Set3.size();
        std::vector<int> Set1Array;
        Set1Array.reserve(setSize1);
        std::copy(Set1.begin(), Set1.end(), std::back_inserter(Set1Array));
        ofs << "Size of Set1: " << setSize1 << endl;
        ofs << "Size of Set2: " << setSize2 << endl;
        ofs << "Size of Set3: " << setSize3 << endl;

        // Serial intersection algorithm
        for (int z = 0; z < numberOfLaunches; z++) {
            set<int> intersectionSet_serial;
            auto start_serial = high_resolution_clock::now();
            intersectionSet_serial = intersection_serial(Set1, Set2, Set3);
            auto stop_serial = high_resolution_clock::now();
            auto duration_serial = duration_cast<microseconds>(stop_serial - start_serial);

            ofs << "Size of intersection Serial: " << intersectionSet_serial.size() << " - Serial execution time: " << duration_serial.count() << " microseconds"<< endl;
        }
        ofs << endl;

        // Pthreads intersection algorithm
        for (int NUM_THREADS : VECTOR_THREADS) {
            ofs << "NUM_THREADS: " << NUM_THREADS << endl;
            for (int z = 0; z < numberOfLaunches; z++) {
                sh = {};
                pthread_mutex_init(&mutex, nullptr);

                int step = ceil(setSize1 / NUM_THREADS);
                ThreadArgs args[NUM_THREADS];
                pthread_t threads[NUM_THREADS];
                auto start_pthreads = high_resolution_clock::now();
                for (int j = 0; j < NUM_THREADS; j++) {
                    args[j].start = j * step;
                    if (j != NUM_THREADS - 1) {
                        args[j].end = (j + 1) * step;
                    } else {
                        args[j].end = setSize1;
                    }
                    args[j].set1Array = Set1Array;
                    args[j].set2 = &Set2;
                    args[j].set3 = &Set3;
                    pthread_create(&threads[j], nullptr, intersection_pthreads, &args[j]);
                }
                for (int j = 0; j < NUM_THREADS; j++)
                    pthread_join(threads[j], nullptr);
                auto stop_pthreads = high_resolution_clock::now();
                auto duration_pthreads = duration_cast<microseconds>(stop_pthreads - start_pthreads);
                pthread_mutex_destroy(&mutex);

                ofs << "Size of intersection Pthreads: " << sh.size() << " - Pthreads execution time: " << duration_pthreads.count() << " microseconds" << endl;
            }
        }
        ofs << endl;

        // OpenMP intersection algorithm
        for (int NUM_THREADS : VECTOR_THREADS) {
            ofs << "NUM_THREADS: " << NUM_THREADS << endl;
            for (int z = 0; z < numberOfLaunches; z++) {
                vector<int> result(setSize1, 0);
                auto start_openmp = high_resolution_clock::now();
                vector<int> intersectionVector_openmp = intersection_openmp(NUM_THREADS, setSize1, Set1Array, Set2, Set3, result);
                auto stop_openmp_1 = high_resolution_clock::now();
                auto duration_openmp_1 = duration_cast<microseconds>(stop_openmp_1 - start_openmp);

                set<int> intersectionSet_openmp;
                for (int a: intersectionVector_openmp) {
                    if (a != 0) {
                        intersectionSet_openmp.insert(a);
                    }
                }
                auto stop_openmp_2 = high_resolution_clock::now();
                auto duration_openmp_2 = duration_cast<microseconds>(stop_openmp_2 - start_openmp);

                ofs << "Size of intersection OpenMP: " << intersectionSet_openmp.size() << " - OpenMP execution time: " << duration_openmp_1.count() << " - OpenMP execution time with answer: " << duration_openmp_2.count() << " microseconds" << endl;
            }
        }
        ofs << endl;
    }

    return 0;
}