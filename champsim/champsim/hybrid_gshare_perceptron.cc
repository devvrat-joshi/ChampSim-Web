#include "ooo_cpu.h"
uint8_t gshare,perceptron;
#define GLOBAL_HISTORY_LENGTH 14
#define GLOBAL_HISTORY_MASK (1 << GLOBAL_HISTORY_LENGTH) - 1
int branch_history_vector[NUM_CPUS];

#define GS_HISTORY_TABLE_SIZE 16384
int gs_history_table[NUM_CPUS][GS_HISTORY_TABLE_SIZE];
int my_last_prediction[NUM_CPUS];

void gshare_initialize_branch_predictor()
{
    int cpu = 0;
    cout << "CPU " << cpu << " GSHARE branch predictor" << endl;

    branch_history_vector[cpu] = 0;
    my_last_prediction[cpu] = 0;

    for(int i=0; i<GS_HISTORY_TABLE_SIZE; i++)
        gs_history_table[cpu][i] = 2; // 2 is slightly taken
}

unsigned int gs_table_hash(uint64_t ip, int bh_vector)
{
    unsigned int hash = ip^(ip>>GLOBAL_HISTORY_LENGTH)^(ip>>(GLOBAL_HISTORY_LENGTH*2))^bh_vector;
    hash = hash%GS_HISTORY_TABLE_SIZE;

    //printf("%d\n", hash);

    return hash;
}

uint8_t gshare_predict_branch(uint64_t ip)
{
    int cpu = 0;
    int prediction = 1;

    int gs_hash = gs_table_hash(ip, branch_history_vector[cpu]);

    if(gs_history_table[cpu][gs_hash] >= 2)
        prediction = 1;
    else
        prediction = 0;

    my_last_prediction[cpu] = prediction;

    return prediction;
}

void gshare_last_branch_result(uint64_t ip, uint8_t taken,uint64_t target)
{
    int cpu = 0;
    int gs_hash = gs_table_hash(ip, branch_history_vector[cpu]);

    if(taken == 1) {
        if(gs_history_table[cpu][gs_hash] < 3)
            gs_history_table[cpu][gs_hash]++;
    } else {
        if(gs_history_table[cpu][gs_hash] > 0)
            gs_history_table[cpu][gs_hash]--;
    }

    // update branch history vector
    branch_history_vector[cpu] <<= 1;
    branch_history_vector[cpu] &= GLOBAL_HISTORY_MASK;
    branch_history_vector[cpu] |= taken;
}

#define GLOBAL_HISTORY_LENGTH 14
#define GLOBAL_HISTORY_MASK (1 << GLOBAL_HISTORY_LENGTH) - 1
int branch_history_vector[NUM_CPUS];

#define GS_HISTORY_TABLE_SIZE 16384
int gs_history_table[NUM_CPUS][GS_HISTORY_TABLE_SIZE];
int my_last_prediction[NUM_CPUS];

void perceptron_initialize_branch_predictor()
{
    int cpu = 0;
    cout << "CPU " << cpu << " GSHARE branch predictor" << endl;

    branch_history_vector[cpu] = 0;
    my_last_prediction[cpu] = 0;

    for(int i=0; i<GS_HISTORY_TABLE_SIZE; i++)
        gs_history_table[cpu][i] = 2; // 2 is slightly taken
}

unsigned int gs_table_hash(uint64_t ip, int bh_vector)
{
    unsigned int hash = ip^(ip>>GLOBAL_HISTORY_LENGTH)^(ip>>(GLOBAL_HISTORY_LENGTH*2))^bh_vector;
    hash = hash%GS_HISTORY_TABLE_SIZE;

    //printf("%d\n", hash);

    return hash;
}

uint8_t perceptron_predict_branch(uint64_t ip)
{
    int cpu = 0;
    int prediction = 1;

    int gs_hash = gs_table_hash(ip, branch_history_vector[cpu]);

    if(gs_history_table[cpu][gs_hash] >= 2)
        prediction = 1;
    else
        prediction = 0;

    my_last_prediction[cpu] = prediction;

    return prediction;
}

void perceptron_last_branch_result(uint64_t ip, uint8_t taken,uint64_t target)
{
    int cpu = 0;
    int gs_hash = gs_table_hash(ip, branch_history_vector[cpu]);

    if(taken == 1) {
        if(gs_history_table[cpu][gs_hash] < 3)
            gs_history_table[cpu][gs_hash]++;
    } else {
        if(gs_history_table[cpu][gs_hash] > 0)
            gs_history_table[cpu][gs_hash]--;
    }

    // update branch history vector
    branch_history_vector[cpu] <<= 1;
    branch_history_vector[cpu] &= GLOBAL_HISTORY_MASK;
    branch_history_vector[cpu] |= taken;
}
//Some Constants:
#define hybrid_history 16390

// HYBRID HISTORY
int HYBRID[hybrid_history];

//Hybrid initialize
void O3_CPU::initialize_branch_predictor(){
    gshare_initialize_branch_predictor();
    perceptron_initialize_branch_predictor();
}

uint8_t O3_CPU::predict_branch(uint64_t ip){
    uint8_t prediction;
    gshare = gshare_predict_branch(ip);
    perceptron = perceptron_predict_branch(ip);
    long long int mask=1;
    long long int hash_value;
    for(int i=0;i<13;i++)mask = (mask<<1)|1;
    hash_value = mask&ip;
    if(HYBRID[hash_value]<2)
        return perceptron;  // perceptron is predictor 2
    else
        return gshare; // gshare is predictor 1
}

void O3_CPU::last_branch_result(uint64_t ip, uint8_t taken, uint64_t target)
{
    long long int mask=1;
    long long int hash_value;
    for(int i=0;i<13;i++)mask = (mask<<1)|1;
    hash_value = mask&ip;
    if(gshare!=taken && perceptron==taken){
        if(HYBRID[hash_value]>0)HYBRID[hash_value] -= 1;
    }
    if(gshare==taken && perceptron!=taken){
        if(HYBRID[hash_value]<3)HYBRID[hash_value] += 1;
    }

    gshare_last_branch_result(ip,taken,target);
    perceptron_last_branch_result(ip,taken,target);
}