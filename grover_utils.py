from typing import List, Tuple
from sympy import And, Not
from qiskit.circuit.library import ZGate, MCXGate, CCXGate
from qiskit import QuantumCircuit, QuantumRegister


def cnf_to_oracle(cnf_formula: And) -> QuantumCircuit:
    """
    Converts a conjunctive normal form (CNF) cnf formula into a quantum oracle circuit.

    Parameters:
    - cnf_formula (And): The CNF cnf formula to be encoded into a quantum oracle.

    Returns:
    - Gate: Quantum gate representing the oracle circuit for the given CNF formula.
    """
    sorted_atoms = sorted(cnf_formula.atoms(), key=str)

    num_variables = len(sorted_atoms)
    num_ancillary = len(cnf_formula.args)
    variable_register = QuantumRegister(num_variables, "v")
    ancillary_register = QuantumRegister(num_ancillary, "a")
    oracle_circuit = QuantumCircuit(variable_register, ancillary_register)

    for i, clause in enumerate(cnf_formula.args):
        mcx_control_target_positions, mcx_gate = createMCXForClause(
            clause, sorted_atoms
        )
        mcx_control_target_positions.append(i + num_variables)
        oracle_circuit.append(mcx_gate, mcx_control_target_positions)

    oracle_circuit.barrier()
    oracle_circuit.x(ancillary_register)

    inverted_oracle_circuit = oracle_circuit.inverse()
    mcz_gate = createMCZGate(num_ancillary)
    oracle_circuit.append(mcz_gate, ancillary_register)
    oracle_circuit = oracle_circuit.compose(inverted_oracle_circuit)

    return oracle_circuit


def build_diffuser(num_of_vars: int) -> QuantumCircuit:
    """
    Builds a quantum circuit for the Grover diffusion operator.

    Parameters:
    - num_of_vars (int): Number of qubits in the quantum register.

    Returns:
    - QuantumCircuit: Quantum circuit representing the Grover diffusion operator.
    """
    qr = QuantumRegister(num_of_vars)
    diffuser_quantum_circuit = QuantumCircuit(qr, name="diffuser")

    diffuser_quantum_circuit.h(qr)
    diffuser_quantum_circuit.x(qr)

    mcz_gate = createMCZGate(num_of_vars)
    diffuser_quantum_circuit.append(mcz_gate, qr)

    diffuser_quantum_circuit.x(qr)
    diffuser_quantum_circuit.h(qr)

    return diffuser_quantum_circuit


def createMCXForClause(clause, sorted_atoms) -> Tuple[List[int], CCXGate]:
    """
    Creates a controlled-X (MCX) gate for a given CNF clause.

    Parameters:
    - clause: The CNF clause for which the MCX gate is created.
    - sorted_atoms: List of sorted atoms in the cnf formula.

    Returns:
    - Tuple[List[int], CCXGate]: A Tuple containing the list of control positions and the MCX gate.
    """
    control_state = ""
    mcx_control_positions = []
    for variable in sorted(clause.args, key=lambda var: str(var).replace("~", "")):
        is_a_not_instance = isinstance(variable, Not)
        control_state += "1" if is_a_not_instance else "0"
        mcx_control_positions.append(
            sorted_atoms.index(variable.args[0] if is_a_not_instance else variable)
        )
    mcx_control_positions.reverse()
    mcx_gate = MCXGate(num_ctrl_qubits=len(clause.args), ctrl_state=control_state)
    return mcx_control_positions, mcx_gate


def createMCZGate(num_qubits: int) -> ZGate:
    """
    Creates a controlled-Z (MCZ) gate with the specified number of control qubits.

    Parameters:
    - num_qubits (int): The number of control qubits for the MCZ gate.

    Returns:
    - ZGate: The controlled-Z gate with the specified number of control qubits.
    """
    return ZGate().control(num_qubits - 1)
