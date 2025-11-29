puts "Scanning for services..."
foreach s [get_service_types] {
    puts "Type: $s"
    foreach p [get_service_paths $s] {
        puts "  Path: $p"
    }
}
exit
