from langchain_text_splitters import RecursiveCharacterTextSplitter

policy_document = """
TechCorp Remote Work Policy

Employees may work remotely up to 3 days per week with manager approval. 
Remote work days must be scheduled in advance and approved by your direct supervisor.
All remote work must comply with company security policies and use approved equipment.
Employees working remotely are expected to maintain regular communication with their team.
Performance expectations remain the same regardless of work location.

Remote work is not a substitute for childcare or eldercare responsibilities.
Employees must have a dedicated workspace free from distractions.
All company equipment must be returned if remote work arrangement is terminated.
"""

splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
chunks = splitter.split_text(policy_document)

print(chunks)