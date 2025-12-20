/**
 * Sanity Schema: Theme
 * Maps to: curric:Theme (subclass of skos:Concept)
 * Properties: skos:prefLabel, skos:definition
 *
 * A cross-cutting theme that can span multiple subjects and content areas.
 */

export default {
  name: 'theme',
  title: 'Theme',
  type: 'document',
  icon: () => '🎨',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "theme-sustainability")',
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
      description: 'The main label for this theme (maps to skos:prefLabel)',
      validation: Rule => Rule.required()
    },
    {
      name: 'definition',
      title: 'Definition',
      type: 'text',
      description: 'Definition of the theme (maps to skos:definition)',
      validation: Rule => Rule.required(),
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
