/**
 * Sanity Schema: Strand
 * Maps to: curric:Strand (subclass of skos:Concept)
 * Properties: skos:prefLabel, skos:definition
 *
 * An organizational strand within a discipline (e.g., "Structure and function of living organisms").
 */

export default {
  name: 'strand',
  title: 'Strand',
  type: 'document',
  icon: () => '🧬',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "strand-structure-function-living-organisms")',
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
      description: 'The main label for this strand (maps to skos:prefLabel)',
      validation: Rule => Rule.required()
    },
    {
      name: 'definition',
      title: 'Definition',
      type: 'text',
      description: 'Definition of the strand (maps to skos:definition)',
      rows: 3
    },
    {
      name: 'discipline',
      title: 'Parent Discipline',
      type: 'reference',
      description: 'The discipline this strand belongs to (maps to skos:broader)',
      to: [{type: 'discipline'}],
      validation: Rule => Rule.required()
    }
  ],
  preview: {
    select: {
      title: 'prefLabel',
      subtitle: 'definition',
      discipline: 'discipline.prefLabel'
    },
    prepare({title, subtitle, discipline}) {
      return {
        title,
        subtitle: `${discipline} - ${subtitle || ''}`
      }
    }
  }
}
