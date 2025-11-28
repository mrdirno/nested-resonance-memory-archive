puts "Scanning..."
set masters [get_service_paths master]
puts "Masters found: $masters"
if {[llength $masters] > 0} {
    puts "Success"
} else {
    puts "Fail"
}
