/**
 * Sanity Schema: Content Descriptor
 * Maps to: curric:ContentDescriptor (subclass of skos:Concept)
 * Properties: skos:prefLabel, skos:definition
 *
 * A statement of knowledge (concept, fact, or skill) within a sub-strand.
 */

export default {
  name: 'contentDescriptor',
  title: 'Content Descriptor',
  type: 'document',
  icon: () => '📝',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "content-descriptor-cells-as-unit-of-living-organism")',
      validation: Rule => Rule.required(),
      options: {
        source: 'prefLabel',
        maxLength: 200,
      }
    },
    {
      name: 'prefLabel',
      title: 'Preferred Label',
      type: 'text',
      description: 'The main content statement (maps to skos:prefLabel)',
      validation: Rule => Rule.required(),
      rows: 3
    },
    {
      name: 'definition',
      title: 'Definition',
      type: 'text',
      description: 'Additional definition or context (maps to skos:definition)',
      rows: 3
    },
    {
      name: 'substrand',
      title: 'Parent Sub-Strand',
      type: 'reference',
      description: 'The sub-strand this content belongs to (maps to skos:broader)',
      to: [{type: 'substrand'}],
      validation: Rule => Rule.required()
    }
  ],
  preview: {
    select: {
      title: 'prefLabel',
      substrand: 'substrand.prefLabel'
    },
    prepare({title, substrand}) {
      const shortTitle = title?.substring(0, 80) + (title?.length > 80 ? '...' : '')
      return {
        title: shortTitle,
        subtitle: substrand
      }
    }
  }
}
