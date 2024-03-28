Built an algorithm to solve  Satisfiability (SAT) Problems with Grover's Algorithm using Qiskit and sympy. 

Here's what each function does : 
- build_grover_circuit : Builds a Grover search algorithm circuit with the given oracle.
- solve_sat_with_grover : Solves a Boolean Satisfiability (SAT) problem using Grover's algorithm.
- cnf_to_oracle : Converts a conjunctive normal form (CNF) cnf formula into a quantum oracle circuit.
- build_diffuser : Builds a quantum circuit for the Grover diffusion operator.
- createMCXForClause : Creates a controlled-X (MCX) gate for a given CNF clause.
- createMCZGate : Creates a controlled-Z (MCZ) gate with the specified number of control qubits.

The tests_grover.ipynb shows the results of 2 SATs.
