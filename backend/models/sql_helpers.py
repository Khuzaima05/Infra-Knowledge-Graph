MODULE_VARIABLES_TABLE = """
CREATE TABLE IF NOT EXISTS module_variables (
    module_id INTEGER NOT NULL,
    variable_id INTEGER NOT NULL,
    PRIMARY KEY (module_id, variable_id),
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (variable_id) REFERENCES variables(id)
);
"""

# This would be used if you want explicit many-to-many relationships
# For now, relationships are tracked via the Relationship table
