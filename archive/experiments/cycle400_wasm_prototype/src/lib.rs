
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn gorkov_potential(amplitude: f64, distance: f64, phase: f64) -> f64 {
    // Minimal proxy for complexity test
    // U = K * (|p|^2 - |grad p|^2)
    // For a single point source, this is trivial, but we simulate the math operations.
    
    let k = 732.0; // Wavenumber approx
    let p = amplitude * (distance * k + phase).cos();
    let grad_p = amplitude * k * (distance * k + phase).sin();
    
    let u = 1.0 * p.powi(2) - 0.5 * grad_p.powi(2);
    u
}

#[wasm_bindgen]
pub fn benchmark_loop(iterations: i32) -> f64 {
    let mut sum = 0.0;
    for i in 0..iterations {
        sum += gorkov_potential(1.0, i as f64 * 0.01, 0.0);
    }
    sum
}
