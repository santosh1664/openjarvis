from openjarvis.personal.graph import PersonalKnowledgeGraph


def test_graph_persists_entities_and_relationships(tmp_path):
    graph = PersonalKnowledgeGraph(tmp_path / "knowledge.db")
    graph.upsert_entity("project", "OpenJarvis", "personal assistant")
    graph.upsert_entity("person", "Alice")
    graph.link("Alice", "works_on", "OpenJarvis")
    graph.close()

    reopened = PersonalKnowledgeGraph(tmp_path / "knowledge.db")
    assert reopened.find("OpenJarvis")[0]["description"] == "personal assistant"
    assert reopened.related("Alice") == [("works_on", "OpenJarvis")]
    reopened.close()
