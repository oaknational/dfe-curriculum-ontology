/**
 * Sanity Schema: Content Sub-Descriptor
 * Maps to: curric:ContentSubDescriptor (subclass of skos:Concept)
 * Properties: skos:prefLabel, skos:definition, curric:example, curric:exampleURL
 *
 * Elaboration or specific detail relating to a content descriptor.
 */

export default {
  name: 'contentSubdescriptor',
  title: 'Content Sub-Descriptor',
  type: 'document',
  icon: () => '📄',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "content-subdescriptor-seasons-detail")',
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
      description: 'The main label (maps to skos:prefLabel)',
      validation: Rule => Rule.required(),
      rows: 2
    },
    {
      name: 'definition',
      title: 'Definition',
      type: 'text',
      description: 'Definition or elaboration (maps to skos:definition)',
      rows: 3
    },
    {
      name: 'contentDescriptor',
      title: 'Parent Content Descriptor',
      type: 'reference',
      description: 'The content descriptor this elaborates on (maps to skos:broader)',
      to: [{type: 'contentDescriptor'}],
      validation: Rule => Rule.required()
    },
    {
      name: 'exampleText',
      title: 'Example Text',
      type: 'text',
      description: 'A text example illustrating this content (maps to curric:example)',
      rows: 3
    },
    {
      name: 'exampleUrl',
      title: 'Example URL',
      type: 'url',
      description: 'A URL example illustrating this content (maps to curric:exampleURL)'
    }
  ],
  preview: {
    select: {
      title: 'prefLabel',
      descriptor: 'contentDescriptor.prefLabel'
    },
    prepare({title, descriptor}) {
      const shortTitle = title?.substring(0, 60) + (title?.length > 60 ? '...' : '')
      const shortDescriptor = descriptor?.substring(0, 40) + (descriptor?.length > 40 ? '...' : '')
      return {
        title: shortTitle,
        subtitle: shortDescriptor
      }
    }
  }
}
