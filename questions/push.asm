// Example assembly: "push constant 7"
@7    // Put the constant in the A-register.
D=A   // Move it aside so it's not clobbered when we...
@SP   // Point the A-register at the stack pointer.
A=M   // and dereference it to find the actual top of stack.
M=D   // Move the constant onto the top of the stack
A=A+1 // Increment the top of stack, and then...
D=A   // ...stash it so that it's not clobbered when we...
@SP   // ...point the A-register at the stack pointer again.
M=D   // and store our new stack pointer.

// Is this too complicated?  Specifically, could I do something
// simpler for the stack pointer increment, like:
// @SP
// M=M+1
