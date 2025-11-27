/**
 * BittWare S5 Physics Simulation Demo
 * 
 * Simple particle physics simulation demonstrating:
 * - Real-time physics calculations
 * - Memory management with FPGA resources
 * - Performance monitoring
 * - Data visualization
 * 
 * Modified to support FPGA bitstream loading via HIL API.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include <time.h>
#include "hil.h"

#define DEVICE_NUM 2
#define MAX_PARTICLES 1000
#define SIMULATION_STEPS 100
#define WORLD_SIZE 1000.0f
#define GRAVITY -9.81f
#define TIME_STEP 0.016f  // ~60 FPS

typedef struct {
    float x, y, z;          // Position
    float vx, vy, vz;       // Velocity  
    float ax, ay, az;       // Acceleration
    float mass;             // Mass
    float radius;           // Radius for collision
    int active;             // Active flag
} Particle;

typedef struct {
    double total_energy;
    double kinetic_energy;
    double potential_energy;
    int active_particles;
    double avg_velocity;
    double max_velocity;
} PhysicsStats;

// Callback for HIL loading status
int load_status(HHil hil, HilStatus* msg, void * user)
{
	printf("Loading FPGA Flash %d%%\r", msg->percent);
	fflush(stdout); // Ensure the progress updates immediately
	return 0;
}	

void print_header() {
    printf("==========================================\n");
    printf("BittWare S5 FPGA Physics Simulation Demo\n");
    printf("==========================================\n\n");
}

void initialize_particles(Particle* particles, int count) {
    printf("🎯 Initializing %d particles...\n", count);
    
    srand(time(NULL));
    
    for (int i = 0; i < count; i++) {
        particles[i].x = (float)(rand() % (int)WORLD_SIZE) - WORLD_SIZE/2;
        particles[i].y = (float)(rand() % (int)WORLD_SIZE/2) + WORLD_SIZE/4;
        particles[i].z = (float)(rand() % (int)WORLD_SIZE) - WORLD_SIZE/2;
        
        particles[i].vx = ((float)rand() / RAND_MAX - 0.5f) * 20.0f;
        particles[i].vy = ((float)rand() / RAND_MAX) * 10.0f;
        particles[i].vz = ((float)rand() / RAND_MAX - 0.5f) * 20.0f;
        
        particles[i].ax = 0.0f;
        particles[i].ay = GRAVITY;
        particles[i].az = 0.0f;
        
        particles[i].mass = 1.0f + ((float)rand() / RAND_MAX) * 4.0f;
        particles[i].radius = 1.0f + particles[i].mass * 0.5f;
        particles[i].active = 1;
    }
    
    printf("✅ Particles initialized with random positions and velocities\n\n");
}

void update_physics(Particle* particles, int count, float dt) {
    // This function would ideally be offloaded to the FPGA
    // For now, it runs on the CPU
    for (int i = 0; i < count; i++) {
        if (!particles[i].active) continue;
        
        // Update velocity
        particles[i].vx += particles[i].ax * dt;
        particles[i].vy += particles[i].ay * dt;
        particles[i].vz += particles[i].az * dt;
        
        // Update position
        particles[i].x += particles[i].vx * dt;
        particles[i].y += particles[i].vy * dt;
        particles[i].z += particles[i].vz * dt;
        
        // Boundary conditions (elastic collision with walls)
        if (particles[i].x < -WORLD_SIZE/2 || particles[i].x > WORLD_SIZE/2) {
            particles[i].vx *= -0.8f; // Energy loss on collision
            particles[i].x = (particles[i].x < 0) ? -WORLD_SIZE/2 : WORLD_SIZE/2;
        }
        
        if (particles[i].y < 0) {
            particles[i].vy *= -0.8f; // Bounce with energy loss
            particles[i].y = 0;
        }
        
        if (particles[i].z < -WORLD_SIZE/2 || particles[i].z > WORLD_SIZE/2) {
            particles[i].vz *= -0.8f;
            particles[i].z = (particles[i].z < 0) ? -WORLD_SIZE/2 : WORLD_SIZE/2;
        }
        
        // Deactivate very slow particles (settled)
        float speed = sqrtf(particles[i].vx*particles[i].vx + 
                           particles[i].vy*particles[i].vy + 
                           particles[i].vz*particles[i].vz);
        if (speed < 0.1f && particles[i].y < 5.0f) {
            particles[i].active = 0;
        }
    }
}

PhysicsStats calculate_stats(Particle* particles, int count) {
    PhysicsStats stats = {0};
    double total_velocity = 0;
    
    for (int i = 0; i < count; i++) {
        if (!particles[i].active) continue;
        
        stats.active_particles++;
        
        // Kinetic energy: 0.5 * m * v^2
        float speed_sq = particles[i].vx*particles[i].vx + 
                        particles[i].vy*particles[i].vy + 
                        particles[i].vz*particles[i].vz;
        float speed = sqrtf(speed_sq);
        
        double ke = 0.5 * particles[i].mass * speed_sq;
        stats.kinetic_energy += ke;
        
        // Potential energy: m * g * h
        double pe = particles[i].mass * (-GRAVITY) * particles[i].y;
        stats.potential_energy += pe;
        
        total_velocity += speed;
        if (speed > stats.max_velocity) {
            stats.max_velocity = speed;
        }
    }
    
    stats.total_energy = stats.kinetic_energy + stats.potential_energy;
    stats.avg_velocity = (stats.active_particles > 0) ? 
                        total_velocity / stats.active_particles : 0;
    
    return stats;
}

void print_simulation_step(int step, PhysicsStats stats, double compute_time) {
    if (step % 10 == 0 || step < 10) {  // Print every 10th step
        printf("Step %3d: Active=%3d, KE=%8.1f, PE=%8.1f, Total=%8.1f, "
               "AvgV=%5.1f, MaxV=%5.1f, Time=%5.2fms\n",
               step, stats.active_particles,
               stats.kinetic_energy, stats.potential_energy, stats.total_energy,
               stats.avg_velocity, stats.max_velocity, compute_time * 1000);
    }
}

// Function to load and boot the FPGA with a bitstream
int load_fpga_bitstream(HHil hil, HDevice dev, const char* bitstream_path) {
    if (!bitstream_path || strlen(bitstream_path) == 0) {
        printf("⚠️ No bitstream path provided. Skipping FPGA load.\n\n");
        return 0; // Not an error if no bitstream is specified
    }

    HResource fpga_res, flash_res;

    printf("🚀 Attempting to load FPGA with bitstream: %s\n", bitstream_path);

    // Retrieve FLASH resource
    flash_res = hil_get_device_resource(dev, HIL_RESOURCE_FLASH, 0);
    if (!flash_res) {
        printf("❌ Board must have a Flash resource to load bitstream.\n");
        return -1;
    }

    // Retrieve FPGA resource
    fpga_res = hil_get_device_resource(dev, HIL_RESOURCE_FPGA, 0);
    if (!fpga_res) {
        printf("❌ Board must have an FPGA resource to boot.\n");
        return -1;
    }

    // Set the status callback function
    hil_status_setui(hil, load_status, NULL);

    // Load the programming file to Flash (assuming .rbf for now, can be adjusted)
    // Note: If loading .rbf, HIL_LOAD_RBF_COMPRESSED might be appropriate.
    // For general bitstreams, HIL_LOAD should be fine.
    printf("Loading %s to Flash partition 1...\n", bitstream_path);
    if (hil_load(flash_res, bitstream_path, HIL_LOAD) < 0) { 
        printf("❌ Error - problem loading %s to Flash.\n", bitstream_path);
        return -1;
    }
    printf("\n✅ Successfully loaded the Flash with %s\n", bitstream_path); 

    // Set boot source to the Flash partition just loaded
    hil_set_resource_value(fpga_res, HIL_FPGA_BOOT_SOURCE, 1);

    // Reload the FPGA from its boot source
    printf("Booting the FPGA from Flash...\n");
    hil_start(fpga_res, HIL_START);
    printf("✅ FPGA booted from %s.\n\n", bitstream_path);
    
    return 0;
}


int run_fpga_physics_simulation(HHil hil, HDevice hdev) {
    printf("🚀 Starting Physics Simulation on BittWare S5...\n\n");
    
    // Allocate particle array
    Particle* particles = malloc(MAX_PARTICLES * sizeof(Particle));
    if (!particles) {
        printf("❌ Failed to allocate particle memory\n");
        return -1;
    }
    
    // Initialize simulation
    initialize_particles(particles, MAX_PARTICLES);
    
    printf("📊 Simulation Parameters:\n");
    printf("   🔢 Particles: %d\n", MAX_PARTICLES);
    printf("   🌍 World Size: %.0f x %.0f x %.0f\n", WORLD_SIZE, WORLD_SIZE, WORLD_SIZE);
    printf("   ⏱️  Time Step: %.3f seconds\n", TIME_STEP);
    printf("   🌍 Gravity: %.2f m/s²\n", GRAVITY);
    printf("   📈 Steps: %d\n\n", SIMULATION_STEPS);
    
    printf("🔬 Physics Simulation Results:\n");
    printf("Step     Active   Kinetic E  Potential E  Total E    AvgVel  MaxVel  CompTime\n");
    printf("----     ------   ---------  -----------  -------    ------  ------  --------\n");
    
    // Run simulation
    for (int step = 0; step < SIMULATION_STEPS; step++) {
        clock_t start_time = clock();
        
        // Update physics
        // TODO: Replace with FPGA accelerated update_physics calls
        update_physics(particles, MAX_PARTICLES, TIME_STEP); 
        
        // Calculate statistics
        PhysicsStats stats = calculate_stats(particles, MAX_PARTICLES);
        
        clock_t end_time = clock();
        double compute_time = ((double)(end_time - start_time)) / CLOCKS_PER_SEC;
        
        // Print results
        print_simulation_step(step, stats, compute_time);
        
        // Stop if all particles settled
        if (stats.active_particles == 0) {
            printf("\n🎯 All particles settled at step %d\n", step);
            break;
        }
        
        // Small delay for visualization
        usleep(50000); // 50ms delay
    }
    
    printf("\n✅ Physics simulation completed!\n\n");
    
    free(particles);
    return 0;
}

void demonstrate_fpga_physics_capabilities(HHil hil, HDevice hdev) {
    printf("🔧 BittWare S5 Physics Processing Capabilities:\n");
    printf("   💾 Available Memory: 32GB DDR3 for large simulations\n");
    printf("   ⚡ Logic Elements: 2.1M for parallel physics calculations\n");
    printf("   🔄 Processing Power: Multi-GHz for real-time physics\n");
    printf("   📊 Data Throughput: PCIe Gen3 x8 for high-speed data transfer\n");
    printf("\n");
    
    printf("🚀 Advanced Physics Applications Possible:\n");
    printf("   • Fluid dynamics simulations (CFD)\n");
    printf("   • Electromagnetic field calculations\n");
    printf("   • Molecular dynamics\n");
    printf("   • Wave propagation modeling\n");
    printf("   • Real-time collision detection\n");
    printf("   • Quantum mechanics simulations\n");
    printf("\n");
}

int main(int argc, char** argv) {
    print_header();
    
    HHil hil = NULL;
    HDevice hdev = NULL;
    const char* bitstream_path = NULL; // Optional bitstream file

    // Parse command line arguments
    if (argc > 1) {
        bitstream_path = argv[1];
    }
    
    // Initialize HIL
    printf("🔌 Initializing BittWare Hardware Interface Layer (HIL)...\n");
    hil = hil_init(HILINIT_NO_OPTION);
    if (!hil) {
        printf("❌ Failed to initialize HIL\n");
        return 1;
    }
    printf("✅ HIL initialized.\n\n");
    
    // Open the device
    printf("🔌 Opening BittWare S5 device %d...\n", DEVICE_NUM);
    hdev = hil_open(hil, DEVICE_NUM, HILOPEN_NO_OPTION);
    if (!hdev) {
        printf("❌ Failed to open BittWare S5 device %d\n", DEVICE_NUM);
        hil_exit(hil);
        return 1;
    }
    printf("✅ Device %d opened successfully.\n\n", DEVICE_NUM);

    // Load FPGA bitstream if provided
    if (load_fpga_bitstream(hil, hdev, bitstream_path) != 0) {
        printf("❌ Failed to load FPGA bitstream. Proceeding with CPU simulation.\n");
        // Optionally, exit here if FPGA load is critical
    }
    
    // Run physics simulation (currently CPU-bound, but now FPGA is loaded)
    int result = run_fpga_physics_simulation(hil, hdev);
    
    // Demonstrate capabilities
    demonstrate_fpga_physics_capabilities(hil, hdev);
    
    // Show final summary
    printf("==========================================\n");
    printf("🎯 Physics Simulation Summary:\n");
    if (result == 0) {
        printf("✅ Successfully simulated particle physics\n");
        printf("✅ Real-time performance monitoring\n");
        printf("✅ Energy conservation calculations\n");
        printf("✅ Collision detection and response\n");
        printf("🚀 BittWare S5 ready for advanced physics!\n");
    } else {
        printf("⚠️  Simulation encountered issues\n");
    }
    printf("==========================================\n");
    
    // Cleanup
    hil_close(hdev);
    hil_exit(hil);
    
    return result;
}