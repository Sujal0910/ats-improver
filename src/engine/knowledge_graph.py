# src/engine/knowledge_graph.py

import networkx as nx

# 1. Hierarchical Taxonomy (Parent -> Child)
SKILL_TAXONOMY = {
    "Cloud Computing": ["AWS", "Azure", "GCP", "Containerization"],
    "Containerization": ["Docker", "Kubernetes"],
    "Backend Development": ["APIs", "Databases", "Python", "Java", "Node.js"],
    "Databases": ["Relational Databases", "NoSQL"],
    "Relational Databases": ["PostgreSQL", "MySQL", "Oracle"],
    "Frontend Development": ["JavaScript", "React", "CSS", "HTML"]
}

# 2. Synonyms (Bidirectional mapping)
SYNONYMS = {
    "K8s": "Kubernetes",
    "Postgres": "PostgreSQL",
    "ReactJS": "React",
    "GCP": "Google Cloud Platform",
    "AWS": "Amazon Web Services"
}

class SkillKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        """Builds the Directed Graph with taxonomic and synonym relationships."""
        # Add hierarchical parent-child relationships
        for parent, children in SKILL_TAXONOMY.items():
            self.graph.add_node(parent, type="category")
            for child in children:
                self.graph.add_node(child, type="skill")
                # Weight of 1.0 represents a hierarchical step down
                self.graph.add_edge(parent, child, weight=1.0) 

        # Add synonym relationships (bidirectional)
        for syn, canonical in SYNONYMS.items():
            self.graph.add_node(syn, type="synonym")
            self.graph.add_node(canonical, type="skill")
            # Weight of 0.0 means they are the exact same concept
            self.graph.add_edge(syn, canonical, weight=0.0)
            self.graph.add_edge(canonical, syn, weight=0.0)

    def get_expanded_skills(self, target_skill: str, depth: int = 2) -> set:
        """
        Takes a broad skill (e.g., 'Cloud Computing') and returns a set of all 
        child skills, sub-skills, and synonyms associated with it.
        """
        # Case-insensitive node matching
        matched_node = next((n for n in self.graph.nodes if n.lower() == target_skill.lower()), None)
        
        if not matched_node:
            return set([target_skill]) # Return the original string if not in graph

        expanded = set([matched_node])
        
        try:
            # 1. BFS Traversal to find all children up to 'depth' levels deep
            edges = nx.bfs_edges(self.graph, matched_node, depth_limit=depth)
            for u, v in edges:
                expanded.add(v)
                
            # 2. Grab synonyms for all terms we just found
            synonyms_to_add = set()
            for skill in expanded:
                for neighbor in self.graph.neighbors(skill):
                    if self.graph[skill][neighbor].get('weight') == 0.0:
                        synonyms_to_add.add(neighbor)
            
            expanded.update(synonyms_to_add)
            
        except nx.NetworkXError:
            pass
            
        return expanded

if __name__ == "__main__":
    print("\n--- Running Phase 2: Skill Knowledge Graph Test ---\n")
    
    kg = SkillKnowledgeGraph()
    
    # Test 1: Expanding a broad category
    test_skill_1 = "Cloud Computing"
    print(f"1. Expanding Broad Category: '{test_skill_1}'")
    expanded_1 = kg.get_expanded_skills(test_skill_1, depth=2)
    print(f"   Graph output: {expanded_1}\n")
    
    # Test 2: Handling a synonym
    test_skill_2 = "K8s"
    print(f"2. Resolving Synonym: '{test_skill_2}'")
    expanded_2 = kg.get_expanded_skills(test_skill_2, depth=1)
    print(f"   Graph output: {expanded_2}\n")

    # Test 3: Deep dive into Backend
    test_skill_3 = "Backend Development"
    print(f"3. Expanding Category: '{test_skill_3}'")
    expanded_3 = kg.get_expanded_skills(test_skill_3, depth=3)
    print(f"   Graph output: {expanded_3}\n")