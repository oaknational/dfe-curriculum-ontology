/**
 * Sanity Schema: Progression
 * Maps to: curric:Progression
 * Properties: rdfs:label, rdfs:comment
 *
 * A progression defines curriculum content relating to a single sub-strand, for a scheme.
 */

export default {
  name: 'progression',
  title: 'Progression',
  type: 'document',
  icon: () => '📈',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "progression-cells-organisation-ks3")',
      validation: Rule => Rule.required(),
      options: {
        source: 'label',
        maxLength: 200,
      }
    },
    {
      name: 'label',
      title: 'Label',
      type: 'string',
      description: 'Progression name (maps to rdfs:label)',
      validation: Rule => Rule.required()
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      description: 'Description of the progression (maps to rdfs:comment)',
      validation: Rule => Rule.required()
    },
    {
      name: 'scheme',
      title: 'Scheme',
      type: 'reference',
      description: 'The scheme this progression belongs to',
      to: [{type: 'scheme'}],
      validation: Rule => Rule.required()
    },
    {
      name: 'substrand',
      title: 'Sub-Strand',
      type: 'reference',
      description: 'The sub-strand this progression relates to',
      to: [{type: 'substrand'}],
      validation: Rule => Rule.required()
    },
    {
      name: 'contentDescriptors',
      title: 'Content Descriptors',
      type: 'array',
      description: 'Content descriptors that are part of this progression',
      of: [{type: 'reference', to: [{type: 'contentDescriptor'}]}],
      validation: Rule => Rule.min(1)
    }
  ],
  preview: {
    select: {
      title: 'label',
      scheme: 'scheme.label',
      substrand: 'substrand.prefLabel'
    },
    prepare({title, scheme, substrand}) {
      return {
        title,
        subtitle: `${scheme} - ${substrand}`
      }
    }
  }
}
