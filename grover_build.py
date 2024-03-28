from typing import Callable, List, Dict
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute
from qiskit.providers import Backend
from sympy import And, Symbol, to_cnf
from grover_utils import build_diffuser


def build_grover_circuit(
    oracle: QuantumCircuit, num_of_vars: int, num_iters: int
) -> QuantumCircuit:
    """
    Builds a Grover search algorithm circuit with the given oracle.

    Parameters:
    - oracle (QuantumCircuit): The oracle circuit for the search problem.
    - num_of_vars (int): The number of variables in the problem.
    - num_iters (int): The number of iterations for the Grover algorithm.

    Returns:
    - QuantumCircuit: The constructed Grover search algorithm circuit.
    """
    variable_register = QuantumRegister(num_of_vars, "v")
    ancillary_register = QuantumRegister(len(oracle.qubits) - num_of_vars, "a")
    classsical_register = ClassicalRegister(num_of_vars, "c")
    grover_circuit = QuantumCircuit(variable_register, ancillary_register, classsical_register)
    diffuser = build_diffuser(num_of_vars)

    grover_circuit.h(variable_register)
    grover_circuit.barrier()

    for _ in range(num_iters):
        grover_circuit = grover_circuit.compose(oracle)
        grover_circuit.barrier()

        grover_circuit = grover_circuit.compose(diffuser, variable_register)
        grover_circuit.barrier()

    return grover_circuit


def solve_sat_with_grover(
    logical_formula: And, cnf_formula_to_oracle: Callable, backend: Backend
) -> List[Dict[Symbol, bool]]:
    """
    Solves a Boolean Satisfiability (SAT) problem using Grover's algorithm.

    Parameters:
    - logical_formula (And): The CNF formula representing the SAT problem.
    - cnf_formula_to_oracle (Callable): A function converting the CNF formula to a quantum oracle.
    - backend (Backend): The quantum backend for executing the Grover algorithm.

    Returns:
    - List[Dict[Symbol, bool]]: List of dictionaries representing solutions to the SAT problem, 
    where each dictionary maps symbols to boolean values.
    """
    cnf_formula = to_cnf(logical_formula)
    nb_atoms = len(cnf_formula.atoms())

    grover_circuit = build_grover_circuit(
        oracle=cnf_formula_to_oracle(cnf_formula),
        num_of_vars=nb_atoms,
        num_iters=3,
    )

    mesure_range = range(nb_atoms)
    grover_circuit.measure(qubit=mesure_range, cbit=mesure_range)

    nb_shots = 100
    job = execute(grover_circuit, backend, shots=nb_shots)
    counts = job.result().get_counts()

    average = nb_shots / (2**nb_atoms)
    solutions = [key for key, value in counts.items() if value > average * 2]
    sorted_atoms = sorted(cnf_formula.atoms(), key=str)
    solutions_dicts = []
    for bit_string in solutions:
        booleans = [bool(int(bit)) for bit in bit_string]
        solutions_dicts.append(dict(zip(sorted_atoms, reversed(booleans))))

    return solutions_dicts
