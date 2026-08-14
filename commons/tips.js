/* THE COMMONS — the tips. Data only; commons/tips.html is the surface and
 * commons/commons.js is the engine both surfaces share.
 *
 * WHAT THIS IS. The thing a journeyman tells an apprentice in the van that
 * nobody ever wrote down. Not gear (that list is gear.js), not paperwork (the
 * forty generator tools already do paperwork), not a how-to. A tip here is a
 * piece of JUDGEMENT — check this before you commit to that — and it earns its
 * place only if somebody had to eat a callback to learn it.
 *
 * THE RAILS, and they are why this page can be trusted:
 *   NO BRANDS. Name the thing, never the label on it.
 *   NO NUMBERS. No torque, depth, slope, clearance, temperature, wire size,
 *     spacing or pressure — ever, as anything. We ship no certified data, so a
 *     tip that needs a number says WHERE THE NUMBER LIVES instead (the print,
 *     the label, the approved submittal). That constraint turned out to make
 *     better tips, not worse ones.
 *   NO CODE CLAIMS. Never "required", never "will fail inspection". Say what
 *     actually happens on the job.
 *   NO SAFETY GUARANTEES, and this is the one that does the most cutting. A tip
 *     a reader could over-trust and get hurt by is not published here at any
 *     quality. Nothing on this page makes a thing safe, dead, isolated or clear.
 *   NON-OBVIOUS. If a first-year already knows it, it is a listicle line.
 *
 * THE PARTITION. `t: ["universal"]` means EVERY trade in the program eats it —
 * a strict bar, because the shared floor is the whole thesis of a commons. A
 * tip three trades share is ONE row with three tags, never three rows. The
 * reader only ever sees the floor plus their own trade, so two rows may say
 * adjacent things as long as no single reader meets both.
 *
 * PROVENANCE. Seeded 2026-08-11 by a fan-out — one pass per trade plus a
 * universal pass — then cut by three independent adversarial lenses: a
 * journeyman rejecting anything a first-year already knows, a rails reviewer
 * rejecting brands / numbers / code / safety-priced-as-money, and a partition
 * reviewer collapsing duplicates and fixing tags. 23 of 130 cut, and the lenses
 * disagreed twice, which is the reason there are three of them:
 *   - The partition lens wanted "ask what's in the slab before anybody shoots
 *     pins" widened from framing to six trades. The rails lens killed it
 *     outright: it frames ASKING as the clearance step before shooting into
 *     post-tension, and a verbal answer is not a scan. Rails won — widening it
 *     would have multiplied the exposure sixfold. (Same class as the
 *     non-contact tester that got cut from gear.js in 2026-08.)
 *   - The partition lens called the two control-line rows one duplicate; the
 *     journeyman had already separated them by TAG — a super's authority to
 *     make every trade lay out from his lines, versus a layout hand's habit of
 *     never pulling off the last wall. Tagged gc-only and framing-only, no
 *     reader ever meets both, which is the only thing the rule protects. Both
 *     stayed.
 * The rails lens also caught nine safety rows the seeders priced as MONEY —
 * refrigerant, gas appliances, energised panels, shared neutrals, phase colours
 * — which is exactly the failure mode a page like this dies of.
 *
 * The seed is the floor, not the ceiling: the field corrects it through the
 * "add a tip" well on the page, and a correction from somebody who does the
 * work outranks anything written here.
 *
 * Author: Aldrin Payopay <aldrin.gdf@gmail.com>
 */

/* THREE ROWS LEFT THE UNIVERSAL FLOOR when trade #9 (creative) arrived:
 * "get the big stuff in before the last opening closes", "shoot your work
 * before it gets covered" (where SHOOT means photograph — the word means the
 * opposite thing to the new trade) and "check the revision, not just the sheet
 * number". None of the three is true of a person who films for a living, and
 * `universal` is a strict claim, not a default bucket. Re-tagged to the eight
 * construction trades, never deleted.
 */
window.COMMONS_TIPS = [
  /* ---- the floor: every trade on the job eats these -------------------- */
  { id: "big-equipment-before-walls", t: ["av", "plumbing", "electrical", "hvac", "low-voltage", "gc", "framing", "roofing"],
    n: "Get the big stuff in before the last opening closes.",
    w: "Racks, tubs, gear sections and units don't fit through a finished door, and cutting the wall back open is somebody's change order." },
  { id: "shoot-before-cover", t: ["av", "plumbing", "electrical", "hvac", "low-voltage", "gc", "framing", "roofing"],
    n: "Shoot your work before it gets covered.",
    w: "Months later your phone is the only proof of what's behind the rock." },
  { id: "existing-damage", t: ["universal"],
    n: "Walk the space and photograph the damage you didn't do.",
    w: "The scratch by the door becomes yours the moment nobody can prove otherwise." },
  { id: "who-holds-keys", t: ["universal"],
    n: "Get the number of whoever actually holds the keys.",
    w: "The man who let you in Monday is off Thursday, and the work stops at a locked door." },
  { id: "stage-material", t: ["universal"],
    n: "Stage your material where nobody else has to move it.",
    w: "Anything in another trade's way gets moved, and it never comes back in one piece." },
  { id: "back-in-and-out", t: ["universal"],
    n: "Park for the load-out, not the walk in.",
    w: "By quitting time the lot's packed in behind you and every heavy thing goes the long way." },
  { id: "moved-it-own-it", t: ["universal"],
    n: "Don't move another trade's work without telling him.",
    w: "The moment your hands are on it, everything that goes wrong with it is yours." },
  { id: "say-it-dont-bury-it", t: ["universal"],
    n: "Found somebody's mistake? Say it before you work around it.",
    w: "Cover it quietly and you inherit it — you were the last one in the room." },
  { id: "flag-the-wait", t: ["universal"],
    n: "The day you start waiting on somebody, put it in writing.",
    w: "A delay nobody was told about turns into your delay at the schedule meeting." },
  { id: "write-the-extra-today", t: ["universal"],
    n: "Write the extra down the day you do it, with the name of whoever asked for it.",
    w: "By month end nobody remembers the conversation, and unwritten work is work you gave away." },
  { id: "punch-your-own", t: ["universal"],
    n: "Punch your own work before somebody punches it for you.",
    w: "Your list costs an hour today; his costs a trip back next month." },
  { id: "closing-walk", t: ["universal"],
    n: "Walk back through everything you opened before you drive off.",
    w: "The cover you left off is the nine o'clock phone call and a free trip." },
  { id: "last-hour", t: ["universal"],
    n: "Don't start the difficult piece in the last hour.",
    w: "Work rushed at quitting time is the piece that comes back, on your own time." },
  { id: "check-the-revision", t: ["av", "plumbing", "electrical", "hvac", "low-voltage", "gc", "framing", "roofing"],
    n: "Check the revision, not just the sheet number.",
    w: "Work built off a superseded drawing comes back out, and nobody reimburses that." },
  { id: "number-off-the-print", t: ["universal"],
    n: "Never build off a number you remember.",
    w: "The dimension you carried over from the last job is the one that gets ripped back out." },

  /* ---- AV ---------------------------------------------------------------- */
  { id: "fixture-cutsheet", t: ["plumbing", "electrical", "hvac", "av"],
    n: "Rough to the approved submittal, not the design drawing.",
    w: "The plan draws a generic unit; the one that got approved moves your rough, and you find out at trim." },
  { id: "fiber-cable-direction", t: ["av"],
    n: "Check which end of a fiber video cable is the source.",
    w: "Those only run one direction. Pull it in backwards and you're pulling the whole run again." },
  { id: "ring-out-air-on", t: ["av"],
    n: "Tune the room with the air running.",
    w: "A dead building at nine at night is not the room anybody sits in at ten on a Tuesday." },
  { id: "client-laptop-test", t: ["av"],
    n: "Test with the customer's own laptop and dongle.",
    w: "Your rig negotiates clean. Their dock is what fails in front of everybody Monday morning." },
  { id: "outline-the-display", t: ["av"],
    n: "Spray your display outline on the wall before anybody roughs it.",
    w: "Otherwise the stat, the strobe and the quad all land inside the panel footprint." },
  { id: "save-the-program", t: ["av", "low-voltage", "hvac", "electrical"],
    n: "Pull a backup of every program before you roll off.",
    w: "When that controller dies in year two, the only copy anywhere is the one you saved." },
  { id: "train-the-booker", t: ["av"],
    n: "Train whoever books the room, not whoever signed the contract.",
    w: "The exec never touches it. The admin who does is your 8am phone call for a year." },
  { id: "camera-backlight", t: ["av"],
    n: "Look at the camera shot with the blinds open.",
    w: "Backlight off that window turns everyone at the table into a silhouette by afternoon." },
  { id: "one-box-out", t: ["av", "low-voltage"],
    n: "Dress the rack so one box can come out alone.",
    w: "Every service call after yours starts by cutting your harness apart to reach one device." },
  { id: "display-slack", t: ["av"],
    n: "Leave enough slack to bring the display off the wall.",
    w: "The next panel's ports are somewhere else, and a tight cable means opening the wall." },
  { id: "firmware-pairs", t: ["av"],
    n: "Keep firmware matched across the chain, not box by box.",
    w: "A transmitter one revision off its receiver drops video in a way that reads as bad cable." },
  { id: "handshake-first", t: ["av"],
    n: "One source plays and another doesn't — suspect the handshake.",
    w: "Content protection dies at the weakest box in the chain and looks exactly like a bad run." },
  { id: "credenza-heat", t: ["av"],
    n: "Ask how the credenza vents before gear goes in it.",
    w: "A sealed cabinet cooks by afternoon, the room starts dropping calls, and AV owns the blame." },
  { id: "ofe-early-power", t: ["av", "low-voltage"],
    n: "Power up owner-furnished gear the day it lands.",
    w: "Half of it's dead or unlicensed, and that lead time lands on your install date." },
  { id: "ceiling-plan-clash", t: ["av", "low-voltage", "electrical"],
    n: "Lay your ceiling plan over the mechanical drawings first.",
    w: "Your device and their diffuser want the same tile, and the one that moves is yours." },
  { id: "real-far-end", t: ["av"],
    n: "Dial a real far end before you call the room done.",
    w: "Local playback proves nothing — echo and mic gain only show up on somebody else's ear." },
  { id: "default-address-collision", t: ["low-voltage", "av"],
    n: "Assume every device out of the box answers to the same address.",
    w: "Put a second one on the network and neither answers; you'll blame the cable for an hour." },
  { id: "clean-the-new-patch-cord", t: ["low-voltage", "av"],
    n: "Clean and inspect every fiber end, including the new patch cord.",
    w: "Factory ends come dirty as often as field ones, and one speck reads as a bad run." },
  { id: "redo-the-ends-first", t: ["low-voltage", "av"],
    n: "When a run fails, redo the ends before you blame the cable.",
    w: "Cable inside a wall rarely goes bad. The punch-down you rushed at quitting time does." },
  { id: "ask-what-circuit", t: ["low-voltage", "av"],
    n: "Ask what circuit the receptacle above the ceiling is on.",
    w: "Land your gear on a light circuit or an occupancy sensor and it reboots every night." },
  { id: "naming-scheme-in-writing", t: ["low-voltage", "av"],
    n: "Get the naming scheme in writing before you print a label.",
    w: "The owner's IT has their own, and re-labelling a finished building is a week nobody's paying for." },
  { id: "hvac-plate-going-up", t: ["hvac", "plumbing", "electrical", "av", "low-voltage"],
    n: "Shoot the data plate the first time you're at the equipment.",
    w: "The office needs model and serial to quote anything, and nobody makes that trip twice for a photo." },
  { id: "gear-crate-day-it-lands", t: ["electrical", "plumbing", "hvac", "av", "low-voltage"],
    n: "Open the crate the day it lands and check it against the submittal.",
    w: "Wrong parts and freight damage found a month later are yours, and the replacement runs the original lead time again." },
  { id: "ring-depth-vs-finish", t: ["electrical", "low-voltage", "plumbing", "av"],
    n: "Ask what the finish is before you set your rough-in depth.",
    w: "Tile, furring or a second layer of board buries your rough, and trim day turns into a hunt for extensions." },
  { id: "measure-the-gear-route", t: ["electrical", "av", "low-voltage", "hvac", "plumbing"],
    n: "Measure the route the gear comes in on, not just the room.",
    w: "A section that clears the room but not the stairwell turns into a rigger and a hole in a wall." },
  { id: "plate-before-the-rockers", t: ["electrical", "low-voltage", "plumbing", "av"],
    n: "Get your nail plates on before the rockers reach that wall, not on your next trip through.",
    w: "The screw goes through your homerun or your PEX on a day you're not there, and it turns up at trim in a painted wall." },

  /* ---- plumbing ---------------------------------------------------------- */
  { id: "reinspection-is-a-week", t: ["gc", "electrical", "plumbing", "hvac", "low-voltage", "roofing"],
    n: "Treat a reinspection as a lost week, not a lost hour.",
    w: "You go back on the end of his list, and every trade stacked behind you sits." },
  { id: "count-test-plugs", t: ["plumbing"],
    n: "Count your test plugs and balls back out.",
    w: "One left in the line is a stoppage nobody can find after the ceiling closes." },
  { id: "old-valve-reseat", t: ["plumbing", "hvac"],
    n: "Assume a valve nobody's turned in years won't reseat.",
    w: "You came to swap a faucet and now you own a building shutdown and a valve nobody stocks." },
  { id: "water-travels", t: ["plumbing"],
    n: "Water shows up where it can fall, not where it leaks.",
    w: "Chase it uphill along the pipe and the joist first, or you'll open ceiling you didn't have to." },
  { id: "dry-trap-smell", t: ["plumbing"],
    n: "Chase a sewer smell to a dry trap first.",
    w: "Floor drains and fixtures nobody uses lose their seal, and you'll open a ceiling for nothing." },
  { id: "press-joint-check", t: ["plumbing"],
    n: "Confirm every press joint actually got pressed.",
    w: "An unpressed fitting holds long enough to pass your walk, then lets go behind finished rock." },
  { id: "cleanout-reach", t: ["plumbing"],
    n: "Put cleanouts where a machine can actually get in.",
    w: "One behind a fixed cabinet is decoration, and the next stoppage means cutting the floor." },
  { id: "old-cast-iron", t: ["plumbing"],
    n: "Price the risk before you cut into old cast iron.",
    w: "The next joint up crumbles, the scope doubles by lunch, and it's your dime unless it's tagged." },
  { id: "flush-before-trim", t: ["plumbing"],
    n: "Flush the line before you set aerators and cartridges.",
    w: "Solder beads and shavings from the rough end up in the first cartridge and come back as a warranty call." },
  { id: "invert-before-dig", t: ["plumbing"],
    n: "Find the tie-in invert before anybody digs.",
    w: "Dig first and you'll learn the existing sits higher than your run, and the whole layout moves." },
  { id: "shoot-the-underground", t: ["plumbing", "electrical", "gc"],
    n: "Photograph the underground with a tape in the shot.",
    w: "The as-built is a guess otherwise, and the guy coring that slab next year is you." },
  { id: "pex-slack", t: ["plumbing"],
    n: "Leave PEX slack at every direction change.",
    w: "It grows and shrinks with hot water; pulled tight it ticks in the wall and rubs through." },
  { id: "panel-directory-is-rumor", t: ["electrical", "plumbing", "hvac"],
    n: "Walk it out yourself — the building's record of what's downstream is a rumor, not a map.",
    w: "People have been in there since it was written, and shutting the wrong thing down buys a tenant's downtime." },
  { id: "duct-wins-the-ceiling", t: ["electrical", "plumbing"],
    n: "Assume the duct wins the ceiling and pick your elevation early.",
    w: "Sheet metal can't offset around you, your pipe can, and whoever hung first still ends up moving." },

  /* ---- electrical -------------------------------------------------------- */
  { id: "hvac-drive-fault", t: ["hvac", "low-voltage", "electrical"],
    n: "Get the fault code or event log off it before anybody resets it.",
    w: "Reset it first and the one thing that would have told you what happened is gone." },
  { id: "shutdown-what-stays-down", t: ["electrical"],
    n: "Before a shutdown, list what won't come back on its own.",
    w: "The call that night is never about the lights — it's the sump, the walk-in, the controller that lost its program." },
  { id: "string-in-every-spare", t: ["electrical", "low-voltage"],
    n: "Leave a string in every spare pipe and tie both ends off.",
    w: "A spare with no string isn't a spare — it's somebody fishing a wall that's already closed." },
  { id: "control-sequence-first", t: ["electrical"],
    n: "Get the control sequence before you rough the switch legs.",
    w: "The print shows a switch; the sequence decides what has to land at it, and the walls close first." },
  { id: "device-orientation-first", t: ["electrical"],
    n: "Ask which way the devices go before you trim a floor.",
    w: "Ground up or down is somebody's preference, not a rule, and finding out late is a floor of re-trim." },
  { id: "morning-of-the-lift", t: ["electrical"],
    n: "Be there the morning the mason lifts that wall.",
    w: "Boxes and pipe he sets by guess come back out of block with a hammer, and that's your day." },
  { id: "call-the-utility-first", t: ["electrical"],
    n: "Call the utility before you set the service, not after.",
    w: "What they'll accept isn't on your prints, and a can in the wrong spot gets moved on your dime." },
  { id: "what-breaker-that-panel-takes", t: ["electrical"],
    n: "Find out what breaker that panel takes before you promise a date.",
    w: "Obsolete and oddball panels take breakers nobody stocks, and the whole tie-in sits waiting on one part." },

  /* ---- HVAC/R ------------------------------------------------------------ */
  { id: "hvac-vac-decay", t: ["hvac"],
    n: "Valve off the pump before you believe the micron reading.",
    w: "Holding is dry; rising then leveling is moisture; rising and never stopping is a leak." },
  { id: "hvac-gauge-cost", t: ["hvac"],
    n: "Don't hook gauges up unless the reading changes what you do.",
    w: "Every hookup bleeds a little charge and lets air in, and on a small system that adds up." },
  { id: "hvac-airflow-first", t: ["hvac"],
    n: "Fix the airflow before you touch the charge.",
    w: "A plugged coil or a slipping belt makes a good charge read wrong, and then you're chasing yourself." },
  { id: "hvac-economizer-first", t: ["hvac"],
    n: "Open the economizer section before you reach for gauges.",
    w: "A stuck damper pulls hot air in all afternoon and reads like a charge problem on gauges." },
  { id: "hvac-drain-blower-on", t: ["hvac"],
    n: "Test the condensate drain with the blower running.",
    w: "A drain that flows fine on a dead unit can hold water once the cabinet's pulling on it." },
  { id: "hvac-watch-defrost", t: ["hvac"],
    n: "Watch a whole defrost before you condemn the control.",
    w: "Boxes get new controllers all the time when it was a heater or a termination switch." },
  { id: "hvac-move-product", t: ["hvac"],
    n: "Get the product moved before you open a box up.",
    w: "Once the case is down the clock is theirs, and lost product lands on your ticket." },
  { id: "hvac-duct-first", t: ["hvac"],
    n: "Get your main duct in before the ceiling fills up.",
    w: "Yours is the biggest thing up there — everybody else can offset around a conflict and you can't." },
  { id: "hvac-out-of-hand", t: ["hvac"],
    n: "Take everything out of hand before you leave the panel.",
    w: "A point left in override runs that way for weeks, and the comfort complaint comes back to you." },

  /* ---- low-voltage & fire ------------------------------------------------ */
  { id: "on-test-reference-number", t: ["low-voltage"],
    n: "Get a reference number every time you put a system on test.",
    w: "It's your only proof you called, and that's what the argument turns on when a dispatch rolls anyway." },
  { id: "test-day-roll-call", t: ["low-voltage"],
    n: "Name every trade that has to stand there on test day.",
    w: "Recall never gets demonstrated when the elevator mechanic isn't there, and the re-test lands on your card." },
  { id: "descriptors-in-room-names", t: ["low-voltage"],
    n: "Write panel descriptors in the building's own room names.",
    w: "Whoever reads the annunciator in the middle of the night knows the room by the sign on the door, not your device tag." },
  { id: "duct-detector-access", t: ["low-voltage"],
    n: "Confirm you can still reach every duct detector after the lid.",
    w: "They get built shut, and getting to one later means cutting somebody's finished ceiling." },
  { id: "read-an-existing-badge", t: ["low-voltage"],
    n: "Read one of the building's existing badges before ordering credentials.",
    w: "The format on the old cards decides the reader order; guess and a whole box shows up useless." },
  { id: "frames-before-the-shop", t: ["low-voltage"],
    n: "Catch door frames before they go to the shop.",
    w: "Prep for a strike or a contact is free at the shop and a grinder in finished steel after." },
  { id: "retest-after-the-closer", t: ["low-voltage"],
    n: "Re-test every opening after the door guy sets the closer.",
    w: "A contact that read closed on your test reads open once the door settles, and that's a nuisance trouble." },
  { id: "reader-on-steel", t: ["low-voltage"],
    n: "A reader landing on steel isn't the same reader as one on drywall.",
    w: "Metal kills the read, and you find that out after the hole is already in the frame." },
  { id: "aim-cameras-after-dark", t: ["low-voltage"],
    n: "Aim and focus cameras after dark, not at lunchtime.",
    w: "IR shifts the focus and lights up whatever's nearest; the daylight shot lies to you." },

  /* ---- GC & site super --------------------------------------------------- */
  { id: "scope-seams-at-buyout", t: ["gc"],
    n: "Nail down who bid the seams — sleeves, access doors, firestop.",
    w: "The scope nobody bid lands on you the week the wall closes." },
  { id: "owner-equipment-list-early", t: ["gc", "framing"],
    n: "Get the owner's equipment list before the walls close.",
    w: "Their mounts and dispensers land months after backing went in, with nothing to screw to." },
  { id: "submittal-is-the-long-lead", t: ["gc"],
    n: "Chase the submittal like it's the long-lead item.",
    w: "Nothing gets fabricated until the review comes back, and that review sits on a desk nobody watches." },
  { id: "date-out-loud-in-huddle", t: ["gc"],
    n: "Make the foreman say his date out loud in the huddle.",
    w: "A date given to you alone gets denied next week; one said in front of his peers sticks." },
  { id: "closeout-before-last-check", t: ["gc"],
    n: "Collect O&Ms, attic stock and warranties before the sub's last check.",
    w: "Nobody answers a closeout call after they've been paid, and you'll chase manuals on your own time." },
  { id: "as-builts-every-month", t: ["gc"],
    n: "Make the subs mark as-builts every month, not at closeout.",
    w: "A year later nobody remembers where the underground went, and the owner finds it with a backhoe." },
  { id: "punch-by-area-not-building", t: ["gc"],
    n: "Punch each area as it finishes, not the whole building at the end.",
    w: "A whole-building list has no leverage, and the crews that made it are already off the job." },
  { id: "laydown-before-first-trailer", t: ["gc"],
    n: "Set the laydown and hoisting plan before the first trailer lands.",
    w: "Whoever parks first owns that yard, and moving him later costs you a day and a favour." },
  { id: "write-the-minutes-yourself", t: ["gc"],
    n: "Write the minutes yourself and put a date on corrections.",
    w: "Un-corrected minutes become the record, and whoever wrote them wins the argument in March." },
  { id: "somebody-elses-calendar", t: ["gc"],
    n: "Track what sits on somebody else's calendar as your real critical path.",
    w: "Permanent power, elevator, fire alarm acceptance — you can't add crew to a queue." },
  { id: "one-set-of-control-lines", t: ["gc"],
    n: "Make every trade lay out from your control lines, not each other.",
    w: "Measuring off somebody else's work compounds the error until the last trade in can't fit." },
  { id: "who-runs-the-crew-tomorrow", t: ["gc"],
    n: "Ask which foreman is running that crew tomorrow, not just today.",
    w: "A new foreman inherits none of your coordination and builds off the old plan." },
  { id: "pay-app-as-schedule-report", t: ["gc"],
    n: "Read the sub's pay application as a schedule report.",
    w: "What he bills says where he thinks he is, and it never matches his look-ahead." },
  { id: "finish-before-owner-stages", t: ["gc"],
    n: "Finish the room before the owner starts staging furniture in it.",
    w: "Once their stuff is in, your punch crew works around it and every scratch is yours." },
  { id: "rake-a-light", t: ["framing", "gc"],
    n: "Don't accept a wall under the work lights.",
    w: "Overhead light flattens everything; the first sunny afternoon shows the ridges to the owner instead of to you." },

  /* ---- framing & drywall ------------------------------------------------- */
  { id: "control-line-not-last-wall", t: ["framing"],
    n: "Pull every dimension off one control line, never off the last wall.",
    w: "Stacking wall off wall drifts, and the far end of the corridor swallows every bit of the error." },
  { id: "look-up-before-you-snap", t: ["framing"],
    n: "Look up at the deck before you snap the floor.",
    w: "A duct main or a beam sitting on your line means framing that wall twice." },
  { id: "wall-type-off-the-schedule", t: ["framing"],
    n: "Read the wall type off the schedule, not off the wall beside it.",
    w: "Every wall on that floor looks the same from the corridor, and a wrong one is full rework." },
  { id: "punchouts-lined-up", t: ["framing"],
    n: "Stand your studs with the punch-outs lined up.",
    w: "Out of line, the next trade drills your studs or bends your flanges to get through." },
  { id: "deflection-track-moves", t: ["framing"],
    n: "Don't pin the stud solid to deflection track.",
    w: "That joint is built to move; screw it tight and the crack shows up over the doors." },
  { id: "welded-or-knockdown", t: ["framing"],
    n: "Find out if frames are welded or knock-down before you frame openings.",
    w: "A welded frame goes in with the wall — learn that after and you're pulling studs back out." },
  { id: "backing-continuous-no-height", t: ["framing"],
    n: "No height given? Run the backing continuous through the range.",
    w: "Costs a sheet of ply now, beats a cut-in and a patch when the number changes." },
  { id: "stock-before-the-frames", t: ["framing"],
    n: "Stock the rooms before the door frames go in.",
    w: "Long board won't turn a finished opening, and every sheet you cut to fit is another joint." },
  { id: "joints-off-opening-corners", t: ["framing"],
    n: "Keep board joints off the corners of openings.",
    w: "That corner is where the building moves, and the crack that starts there is your callback." },
  { id: "pull-the-missed-screws", t: ["framing"],
    n: "Back out the screws that missed — don't just shoot another.",
    w: "A screw hanging in board with nothing behind it works loose and telegraphs through the finish." },
  { id: "wet-frame-pops", t: ["framing"],
    n: "Check the lumber's dried out before you board over it.",
    w: "Wet framing shrinks once the heat comes on, and every fastener pops through the paint." },

  /* ---- roofing ------------------------------------------------------------
     Added 2026-08-13. Roofing had a chip on this page from 2026-08-12 and not one
     tip written for it — see gear.js for how that stayed green, and §SCARS.

     THE HEIGHT RAIL DID MORE CUTTING HERE THAN ON ANY OTHER TRADE, and the pattern
     worth naming is not the obvious one. Almost nothing proposed said "be safe";
     what it did was PRICE A SAFETY EXPOSURE AS MONEY — a shutdown, a callback, a
     claim — which is worse than an honest safety tip, because it teaches a reader
     to weigh a hazard as a cost he can decide to eat. Killed on exactly that:
     the fresh-air intakes (people breathing what you run, priced as your lost
     section — unsalvageable, no rewrite exists), and a bare foot in the grass
     itemised beside a tire and a mower blade. The subtlest one survived a rewrite
     rather than dying: "find out what the deck is" had its reason pointed at a
     truck driving for material, and "what is the deck under this section" is the
     fall-through question — a reader who prices that delay and eats it has been
     taught by this page to skip the check and walk the section. It now points at
     the approved submittal, which is where the number lives anyway.

     Also killed: three re-tags whose SENTENCES belong to other trades even though
     the judgement travels (a roofer has no crate, no rough and no trim day, and
     "chase it uphill along the pipe and the joist" points him at the wrong
     geometry entirely — roof water runs the deck and the insulation), and two rows
     that collided inside this trade's own lane, since a roofer already reads the
     universal floor: a second end-of-day cleanup row, and a tear-off-order row
     that restated "don't start the difficult piece in the last hour". */
  { id: "ask-when-it-leaks", t: ["roofing"],
    n: "Ask when it leaks before you go up.",
    w: "Driven rain, a day later, and only in the cold are three different leaks, and you'll spend the day at the wrong end of the building." },
  { id: "water-test-low-first", t: ["roofing"],
    n: "Wet one area at a time, starting at the low end.",
    w: "Wet the whole roof at once and you've proven nothing — and you can't take it back off, so now you're waiting on it to dry." },
  { id: "leave-the-strainer-on", t: ["roofing"],
    n: "Don't pull a strainer to make the water move faster.",
    w: "Tear-off grit goes down the leader and stops somewhere inside the building nobody can reach, and the next storm comes out of a ceiling." },
  { id: "tell-below-before-tearoff", t: ["roofing", "gc"],
    n: "Before you open a section, tell whoever works under it.",
    w: "Rust and grit come out of the deck and the light fixtures all day, and the complaint is never water — it's dust in somebody's stock." },
  { id: "open-to-what-landed", t: ["roofing"],
    n: "Size the day's opening off the material already on the roof, not what's on the truck.",
    w: "A load that slides a day turns your tear-off into a night of temporary work, and you'll do that section twice." },
  { id: "cuts-low-and-at-walls", t: ["roofing"],
    n: "Take your test cuts low and against the walls, not in the middle of the field.",
    w: "Wet insulation and the extra layer sit low and at the walls — cut only the dry middle and you find them after your number's in." },
  { id: "what-deck-is-it", t: ["roofing"],
    n: "Find out what the deck is under every section, not just the one you cut open.",
    w: "One building holds more than one deck — the original, the addition, the patch — and your approved submittal was written for one of them." },
  { id: "tie-in-early", t: ["roofing"],
    n: "Cut the tie-in to the existing roof open early, not on the day you have to make it.",
    w: "The old assembly isn't on any drawing, and the answer comes from a consultant or the manufacturer's rep — on their schedule, not yours." },
  { id: "who-covers-your-flashing", t: ["roofing"],
    n: "Find out who sets what goes over your flashing at every wall, and when he's coming.",
    w: "Your half is done and open at the same time, and if he comes next month every rain in between gets filed under the roofer." },
  { id: "weather-call-owner", t: ["roofing"],
    n: "Find out who makes the weather call and when he makes it.",
    w: "Settle it before the truck rolls, or it gets made late by whoever wants the day — and it's your deck that's open." },
  { id: "magnet-after-the-dumpster", t: ["roofing"],
    n: "Run the magnet again the morning after the dumpster leaves, not the night before.",
    w: "The truck drags out whatever was under it, and on a house the callback is never the roof — it's a tire or a mower blade." },

  /* ---- creative / video ---------------------------------------------------
     Non-obvious by the same bar as every other trade: if a first-year already
     knows it, it is a listicle line. Nothing here states what a licence or a
     release permits, and nothing names a platform, a codec or a product. */
  { id: "room-tone-before-breakdown", t: ["creative"],
    n: "Record thirty seconds of room tone before anyone starts packing.",
    w: "The mix needs it to hide every edit in the interview, and it is the one thing you can never go back for." },
  { id: "roll-early-hold-late", t: ["creative"],
    n: "Roll before you call it and hold after you cut it.",
    w: "Those handles are what let the edit breathe. Without them every dissolve is a fight." },
  { id: "logo-and-fonts-day-one", t: ["creative"],
    n: "Ask for the logo, the fonts and the hex codes on day one, in writing.",
    w: "Ask at the end and they arrive the night before delivery, in the wrong format, from someone who has left." },
  { id: "spell-the-names", t: ["creative"],
    n: "Get names and titles spelled by the person on camera, not by whoever booked them.",
    w: "A wrong lower third is the one mistake the whole company sees, and it is always caught after delivery." },
  { id: "kill-the-hvac", t: ["creative"],
    n: "Get the HVAC shut off before you set up — and get the contact's mobile to turn it back on.",
    w: "The hum sits under every word, and the building nobody could switch back on is a story you only star in once." },
  { id: "who-signs-off", t: ["creative"],
    n: "Find out who signs off before you shoot, not after.",
    w: "The person in the room is usually not the person with notes, and their boss's notes arrive after picture lock." },
  { id: "shoot-the-cutaway-first", t: ["creative"],
    n: "Grab the cutaways before the interview, not after.",
    w: "Afterwards they are already checking their phone, and the cutaway is what saves the answer that rambled." },

  /* ---- concrete: trade #10 ---------------------------------------------- */
  { id: "walk-it-before-the-top-mat", t: ["concrete"],
    n: "Walk it with the electrician and the plumber before the top mat goes on.",
    w: "Everything they owe you disappears under the steel, and after that nobody can see what is missing until it is under six inches of mud." },
  { id: "shoot-the-steel", t: ["concrete"],
    n: "Photograph the steel, the embeds and the sleeves before you place.",
    w: "It is the only look anybody will ever get. When the question comes in October, your phone is the whole answer." },
  { id: "write-the-truck-down", t: ["concrete"],
    n: "Write every truck down as it lands.",
    w: "Ticket, time on the ground, time it finished. Three weeks later the yardage argument is a document on your side or two people's memories on theirs." },
  { id: "who-called-for-water", t: ["concrete"],
    n: "Anything added on the ground goes on the ticket with the name of whoever called for it.",
    w: "It is the first question asked when a cylinder comes back low, and the only wrong answer is that nobody wrote it down." },
  { id: "wash-out-where-you-said", t: ["concrete"],
    n: "Settle the washout before the first truck, and hold everybody to it.",
    w: "A driver rinsing a chute wherever he stops is your cleanup, your stain on somebody's new asphalt, and occasionally your fine." },
  { id: "who-is-calling-the-inspection", t: ["concrete"],
    n: "Find out who is calling the inspection and when it is actually scheduled.",
    w: "Not who said they would call it. A crew standing at six with a truck turning is the most expensive way to learn nobody did." },
  { id: "grade-set-before-the-truck", t: ["concrete"],
    n: "Screeds, grade and your finish gear are set before the truck, not while it turns.",
    w: "Everything you do after the mud is on the ground you do against a clock you do not control." },
  { id: "nobody-strips-until-somebody-says", t: ["concrete"],
    n: "Nobody strips it, loads it or drives on it until whoever owns that call says so.",
    w: "It is not your judgment and it is not the calendar's — it is the person on the job whose call that is, in writing if you can get it." },
  { id: "order-the-tail-early", t: ["concrete"],
    n: "Order the tail end before you need it.",
    w: "The last truck is the one that shows up short, late, or not at all, and a cold joint you did not plan is the most expensive line on the job." },
  { id: "plan-how-you-walk-out", t: ["concrete"],
    n: "Decide how the finish crew walks out of the pour before it starts.",
    w: "Everybody plans how the mud gets in. The crew that has to back out across it is what turns a good slab into a patched one." }
];
