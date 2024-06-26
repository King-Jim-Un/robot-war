# Purpose

This file exists to provide a place to collect notes about the kinds of things
that will need to be implemented.


## Modes
The intent is to have multiple modes or levels at which a player can work,
starting with mode0, beginner's mode, and advancing to modeN, an as-yet-
undetermined level.

With the clear exception of infinite acceleration in the lower levels, features
are cumulative.

### Mode0
This is training mode.

There are no customizations to the 'bots in this mode.

Movement will be orthoginal only, meaning turns will only be 90°.
 - There is no diagonal movement in mode0.
 - Consider possibly having the `turn()` function accept `N`, `E`, `S`, `W`
   to set an absolute direction, which could carry forward to the higher modes.

Movement is "at speed" rather than "with acceleration".
 - Probably restrict 'bots to slower speeds, or maybe make 'bots go to one speed
   before they increase it.
 - Assume (mathematically) that acceleration is infinite at this level. Boom,
   you're there.
 - "Negative" movement is permitted, though possibly at reduced top speed?
 - A body in motion remains in motion until a force acts on it to stop it.

There would be a `full_stop()` command with no consideration of deceleration.

Activities would be sequential:
 - Only turning while turning
 - Only moving while moving
 - Only shooting while shooting
 - Only scanning while scanning
 - Only self-assess while self-assessing

Scanning is **not** orthoginal.
 - Scanning returns polar coordinates (angle, range) of object
   - Should that also include size estimate of object? If there's some
     possibility that arenas will eventually have obstacles (walls, blocks,
     pits, etc.) then that would be useful. It might not be necessary at mode0,
     but it would get people in the habit of receiving the data.

There are no interrupts to one's program in mode0.
 - You told your 'bot to go forward for a while and then stop? That's what you
   get. If you hit a wall, you stop &mdash; just maybe a little before you
   expected to &mdash; even if your treads are still spinning.
 - You take damage? Heck, you hardly even notice it. “Damn the torpedoes!
   Jouett, full speed! Four bells, Captain Drayton!” 

### Mode1
Mode1 gets a little more real-world in its physics and movement.

Movement is no longer orthoginal.
 - You can still specify a cardinal direction to set yourself to that direction
 - You can now also specify a turn in degrees (positive or negative)

Acceleration is no longer infinite.
 - There is now a maximum acceleration that a 'bot can produce. (In later modes
   this might be a different value based on configuration.)
 - You can now specify that you wish to go to any speed (rather than successive
   instant increments to that speed), but you need to either specify an
   acceleration rate or accept your max as default.
 - The `full_stop()` command now also considers deceleration, though the max
   deceleration rate is likely to be higher than the max acceleration rate for
   any given 'bot.

Activities remain sequential.

Welcome to interrupts.
 - You now get an interrupt (maybe an exception?) when you take damage.
 - You now get an interrupt when you come into contact with something.

### Mode2
Here is where you get concurrent activities. You will be able to scan or shoot
while you're moving, for example.

Arena-generated damage, i.e., collision damage from hitting a wall too fast.

### Mode3
Customizations.

The intent is that users will have a budget they can use to modify their basic
'bot:
 - Faster motors for higher speeds
 - Stronger motors for higher acceleration
 - Better brakes for faster stopping
 - Faster scanners
 - Better/different weapons
 - Armor

Class(?) or Budget(?) &mdash; There will need to be some grouping of 'bots so
that some well-heeled Spike who spent a lot on his 'bot can't just crush some
Timmy who has just graduated to mode3.

## Levels
Within each mode, there will be three levels providing environments in which to
learn how to manage the 'bots features at that mode.

### Explore
This is the most fundamental level. You're alone in an arena, and all you can
do is wonder around. You can learn how to find and recognize walls and
obstructions and move around them.

### Perform
This level provides some small puzzle for you, such as "blow up this thing that
may or may not be shooting back at you" or "push this blob into a pit" This ups
the stakes a bit on Explore, especially if you have a rather dumb AI shooting
at you.

### Survive
This level pits you against a comparably resourced 'bot. A mode0 'bot would
never face a mode1 'bot, and presumably by mode3 you'll have 'bots built with
comparable budgets.

## Arenas

### Shape

As mentioned previously, the mode0 arena is likely to just be a square, since
that's easy on the math, or circle, since that's easy on the brain (and keeps
you from getting stuck in a corner).

### Obstacles

 - **Blocks**: Remember the old Tank Battle games where there were big cubes
   and pyramids out in the battlefield? Yeah, those.

 - **Walls**: Nominally thin, but obscuring vision and stopping movement. The
   outside edges of the arena are made of this indestructible stuff. It is
   conceivable that arenas could even be built as mazes or labrynths using
   walls.

 - **Fences**: Think of these as half-height walls, which block movement but
   but not vision or weapons.

 - **Pits**: Yeah, you saw that coming. Or, maybe you didn't. It would make
   requests for scanning more complicated, since you'd have to be looking down
   as well as out.

 - **Hazards**? Think: RoboRally
   - Lasers
   - Flamers
   - Crushers
   - Pushers
   - Spiked walls that deal more damage on collision?

## Customizations
The obvious customization path is of the 'bots. But I think we could probably
open up the doors to customized arenas, where someone could configure the
shape and obstacles in the arena at the Explore and Perform levels. This could
open up the notion of single-bot missions in the Perform level where people
compete for the best time to solve it.
