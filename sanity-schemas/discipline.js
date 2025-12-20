/**
 * Sanity Schema: Discipline
 * Maps to: curric:Discipline (subclass of skos:Concept)
 * Properties: skos:prefLabel, skos:definition, skos:scopeNote
 *
 * An organizational discipline in the knowledge taxonomy (e.g., Science, Mathematics).
 */

export default {
  name: 'discipline',
  title: 'Discipline',
  type: 'document',
  icon: () => '🔬',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "discipline-science")',
      validation: Rule => Rule.required(),
      options: {
        source: 'prefLabel',
        maxLength: 100,
      }
    },
    {
      name: 'prefLabel',
      title: 'Preferred Label',
      type: 'string',
      description: 'The main label for this discipline (maps to skos:prefLabel)',
      validation: Rule => Rule.required()
    },
    {
      name: 'definition',
      title: 'Definition',
      type: 'text',
      description: 'Formal definition of the discipline (maps to skos:definition)',
      validation: Rule => Rule.required(),
      rows: 3
    },
    {
      name: 'scopeNote',
      title: 'Scope Note',
      type: 'text',
      description: 'Additional context about the scope and application (maps to skos:scopeNote)',
      rows: 3
    }
  ],
  preview: {
    select: {
      title: 'prefLabel',
      subtitle: 'definition'
    }
  }
}
