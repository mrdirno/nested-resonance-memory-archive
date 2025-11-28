# JTAG Bridge Server (Tcl implementation for System Console)
# Listens on TCP 5000 and proxies commands to JTAG Master

set PORT 5000

# 1. Initialize JTAG
puts "Scanning for JTAG Master..."
set retry_count 0
while {$retry_count < 5} {
    set master_paths [get_service_paths master]
    if {[llength $master_paths] > 0} {
        break
    }
    puts "No master found. Retrying..."
    after 1000
    incr retry_count
}

if {[llength $master_paths] == 0} {
    puts "Error: No JTAG Master found after retries."
    puts "DEBUG: Services found: [get_service_paths master]"
    return
}
set master_path [lindex $master_paths 0]
puts "JTAG Master: $master_path"
open_service master $master_path

# 2. Server Logic
proc start_server {port} {
    set s [socket -server accept_conn $port]
    puts "Listening on port $port..."
    vwait forever
}

proc accept_conn {sock addr port} {
    puts "Connection from $addr:$port"
    fconfigure $sock -buffering line
    fileevent $sock readable [list handle_data $sock]
}

proc handle_data {sock} {
    global master_path
    if {[eof $sock]} {
        puts "Client disconnected."
        close $sock
        return
    }
    
    gets $sock line
    if {$line eq ""} { return }
    
    # Parse Command
    set parts [split $line " "]
    set cmd [string toupper [lindex $parts 0]]
    
    if {$cmd eq "PING"} {
        puts $sock "PONG"
    } elseif {$cmd eq "WR"} {
        # WR <addr> <val>
        if {[llength $parts] == 3} {
            set addr [lindex $parts 1]
            set val [lindex $parts 2]
            # Handle hex strings
            if {[scan $val %x v] == 1} {
                 if {[catch {master_write_32 $master_path $addr [list $v]} err]} {
                     puts $sock "ERR: $err"
                 } else {
                     puts $sock "OK"
                 }
            } else {
                puts $sock "ERR: Invalid Value"
            }
        } else {
            puts $sock "ERR: WR needs 2 args"
        }
    } elseif {$cmd eq "RD"} {
        # RD <addr>
        if {[llength $parts] == 2} {
            set addr [lindex $parts 1]
            if {[catch {master_read_32 $master_path $addr 1} val]} {
                puts $sock "ERR: $val"
            } else {
                puts $sock [format "0x%08X" [lindex $val 0]]
            }
        } else {
            puts $sock "ERR: RD needs 1 arg"
        }
    } else {
        puts $sock "ERR: Unknown Command"
    }
    flush $sock
}

# 3. Start
start_server $PORT