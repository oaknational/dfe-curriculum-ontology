/**
 * Sanity Schema: Sub-Strand
 * Maps to: curric:SubStrand (subclass of skos:Concept)
 * Properties: skos:prefLabel, skos:definition
 *
 * A sub-division of a strand (e.g., "Cells and organisation").
 */

export default {
  name: 'substrand',
  title: 'Sub-Strand',
  type: 'document',
  icon: () => '🔗',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "substrand-cells-organisation")',
      validation: Rule => Rule.required(),
      options: {
        source: 'prefLabel',
        maxLength: 150,
      }
    },
    {
      name: 'prefLabel',
      title: 'Preferred Label',
      type: 'string',
      description: 'The main label for this sub-strand (maps to skos:prefLabel)',
      validation: Rule => Rule.required()
    },
    {
      name: 'definition',
      title: 'Definition',
      type: 'text',
      description: 'Definition of the sub-strand (maps to skos:definition)',
      rows: 3
    },
    {
      name: 'strand',
      title: 'Parent Strand',
      type: 'reference',
      description: 'The strand this sub-strand belongs to (maps to skos:broader)',
      to: [{type: 'strand'}],
      validation: Rule => Rule.required()
    }
  ],
  preview: {
    select: {
      title: 'prefLabel',
      subtitle: 'definition',
      strand: 'strand.prefLabel'
    },
    prepare({title, subtitle, strand}) {
      return {
        title,
        subtitle: `${strand} - ${subtitle || ''}`
      }
    }
  }
}
