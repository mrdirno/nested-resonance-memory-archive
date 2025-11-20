"""
DUALITY-ZERO-V2 Fractal Agent
Lightweight agent class for NRM simulation experiments

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>

This module provides the FractalAgent class for NRM experiments.
Agents have energy dynamics and can be managed by population.
"""


class FractalAgent:
    """
    Minimal fractal agent for NRM simulation.

    Attributes:
        agent_id: Unique identifier for the agent
        population_id: ID of the population this agent belongs to
        energy: Current energy level (0.0 to 2.0)
        depth: Hierarchical depth (default 0)
        memory: Pattern memory storage
    """

    def __init__(
        self,
        agent_id: str,
        population_id: int = 0,
        energy: float = 1.0,
        depth: int = 0
    ):
        """
        Initialize a fractal agent.

        Args:
            agent_id: Unique identifier
            population_id: Population this agent belongs to
            energy: Initial energy level (default 1.0)
            depth: Hierarchical depth (default 0)
        """
        self.agent_id = agent_id
        self.population_id = population_id
        self.energy = energy
        self.depth = depth
        self.memory = {}
        self.birth_cycle = 0
        self.compositions = 0
        self.decompositions = 0

    def consume_energy(self, amount: float) -> bool:
        """
        Consume energy. Returns False if agent dies (energy <= 0).

        Args:
            amount: Energy to consume

        Returns:
            True if agent survives, False if energy depleted
        """
        self.energy -= amount
        return self.energy > 0

    def recharge_energy(self, amount: float, cap: float = 2.0) -> None:
        """
        Recharge energy up to cap.

        Args:
            amount: Energy to add
            cap: Maximum energy level (default 2.0)
        """
        self.energy = min(self.energy + amount, cap)

    def __repr__(self) -> str:
        return f"FractalAgent({self.agent_id}, pop={self.population_id}, E={self.energy:.2f})"


class SimulationInterface:
    """
    Interface for managing NRM simulation state.

    Manages populations of FractalAgents with energy dynamics,
    migration, and metric logging to SQLite database.
    """

    def __init__(
        self,
        db_path: str = None,
        n_populations: int = 10,
        mode: str = "HIERARCHICAL"
    ):
        """
        Initialize simulation interface.

        Args:
            db_path: Path to SQLite database for metrics
            n_populations: Number of populations to manage
            mode: Simulation mode (HIERARCHICAL or FLAT)
        """
        import sqlite3

        self.db_path = db_path
        self.n_populations = n_populations
        self.mode = mode
        self.energy_config = {
            "E_consume": 0.5,
            "E_recharge": 1.0
        }

        # Population storage: list of lists of agents
        self.populations = [[] for _ in range(n_populations)]

        # Database connection
        self.conn = None
        if db_path:
            self.conn = sqlite3.connect(db_path)
            self._init_database()

    def _init_database(self) -> None:
        """Initialize database tables for metrics."""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cycle_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle INTEGER NOT NULL,
                population INTEGER NOT NULL,
                energy_total REAL NOT NULL,
                n_compositions INTEGER,
                n_decompositions INTEGER,
                timestamp REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiment_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT NOT NULL
            )
        """)

        self.conn.commit()

    def add_agent(self, agent: FractalAgent, population_id: int = None) -> None:
        """
        Add an agent to a population.

        Args:
            agent: FractalAgent to add
            population_id: Target population (uses agent's population_id if None)
        """
        if population_id is None:
            population_id = agent.population_id

        if 0 <= population_id < self.n_populations:
            agent.population_id = population_id
            self.populations[population_id].append(agent)

    def get_population_agents(self, population_id: int) -> list:
        """
        Get all agents in a population.

        Args:
            population_id: Population to query

        Returns:
            List of agents in the population
        """
        if 0 <= population_id < self.n_populations:
            return self.populations[population_id]
        return []

    def remove_agent(self, agent_id: str, population_id: int) -> bool:
        """
        Remove an agent from a population.

        Args:
            agent_id: ID of agent to remove
            population_id: Population to remove from

        Returns:
            True if agent was removed, False if not found
        """
        if 0 <= population_id < self.n_populations:
            pop = self.populations[population_id]
            for i, agent in enumerate(pop):
                if agent.agent_id == agent_id:
                    pop.pop(i)
                    return True
        return False

    def migrate_agent(
        self,
        agent_id: str,
        source_pop: int,
        target_pop: int
    ) -> bool:
        """
        Move an agent between populations.

        Args:
            agent_id: ID of agent to migrate
            source_pop: Source population
            target_pop: Target population

        Returns:
            True if migration successful, False otherwise
        """
        if not (0 <= source_pop < self.n_populations):
            return False
        if not (0 <= target_pop < self.n_populations):
            return False

        # Find agent in source
        source = self.populations[source_pop]
        for i, agent in enumerate(source):
            if agent.agent_id == agent_id:
                # Remove from source
                agent = source.pop(i)
                # Add to target
                agent.population_id = target_pop
                self.populations[target_pop].append(agent)
                return True

        return False

    def log_cycle_metrics(
        self,
        cycle: int,
        population: int,
        energy_total: float,
        n_compositions: int = 0,
        n_decompositions: int = 0
    ) -> None:
        """
        Log metrics for a cycle to the database.

        Args:
            cycle: Cycle number
            population: Total population count
            energy_total: Total energy in system
            n_compositions: Number of composition events
            n_decompositions: Number of decomposition events
        """
        if self.conn:
            import time
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO cycle_metrics
                (cycle, population, energy_total, n_compositions, n_decompositions, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cycle, population, energy_total, n_compositions, n_decompositions, time.time()))
            self.conn.commit()

    def get_total_population(self) -> int:
        """Get total agent count across all populations."""
        return sum(len(pop) for pop in self.populations)

    def get_total_energy(self) -> float:
        """Get total energy across all agents."""
        return sum(
            sum(agent.energy for agent in pop)
            for pop in self.populations
        )

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None


# Alias for backward compatibility
RealityInterface = SimulationInterface
