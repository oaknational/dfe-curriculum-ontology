/**
 * Sanity Schema: Scheme
 * Maps to: curric:Scheme
 * Properties: rdfs:label, rdfs:comment
 *
 * A scheme defines curriculum content for a sub-subject at a specific key stage.
 */

export default {
  name: 'scheme',
  title: 'Scheme',
  type: 'document',
  icon: () => '📋',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "scheme-science-key-stage-3")',
      validation: Rule => Rule.required(),
      options: {
        source: 'label',
        maxLength: 150,
      }
    },
    {
      name: 'label',
      title: 'Label',
      type: 'string',
      description: 'Scheme name (maps to rdfs:label)',
      validation: Rule => Rule.required()
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      description: 'Description of the scheme (maps to rdfs:comment)',
      validation: Rule => Rule.required()
    },
    {
      name: 'subsubject',
      title: 'Sub-Subject',
      type: 'reference',
      description: 'The sub-subject this scheme belongs to',
      to: [{type: 'subsubject'}],
      validation: Rule => Rule.required()
    },
    {
      name: 'keyStage',
      title: 'Key Stage',
      type: 'reference',
      description: 'The key stage this scheme covers',
      to: [{type: 'keyStage'}],
      validation: Rule => Rule.required()
    },
    {
      name: 'contentDescriptors',
      title: 'Content Descriptors',
      type: 'array',
      description: 'Content descriptors included in this scheme',
      of: [{type: 'reference', to: [{type: 'contentDescriptor'}]}],
      validation: Rule => Rule.required().min(1)
    }
  ],
  preview: {
    select: {
      title: 'label',
      subsubject: 'subsubject.label',
      keyStage: 'keyStage.label'
    },
    prepare({title, subsubject, keyStage}) {
      return {
        title,
        subtitle: `${subsubject} - ${keyStage}`
      }
    }
  }
}
