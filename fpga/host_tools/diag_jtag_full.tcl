puts "--- Full JTAG Diagnostics ---"
puts "All Services:"
foreach service [get_service_types] {
    set paths [get_service_paths $service]
    if {[llength $paths] > 0} {
        puts "  Service: $service"
        foreach p $paths {
            puts "    $p"
        }
    }
}
