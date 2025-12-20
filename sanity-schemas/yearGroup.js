/**
 * Sanity Schema: Year Group
 * Maps to: curric:YearGroup
 *
 * A year group within a key stage.
 */

export default {
  name: 'yearGroup',
  title: 'Year Group',
  type: 'document',
  icon: () => '📅',
  fields: [
    {
      name: 'id',
      title: 'ID',
      type: 'slug',
      description: 'Unique identifier (e.g., "year-1", "year-7")',
      validation: Rule => Rule.required(),
      options: {
        source: 'label',
        maxLength: 50,
      }
    },
    {
      name: 'label',
      title: 'Label',
      type: 'string',
      description: 'Display name (e.g., "Year 1")',
      validation: Rule => Rule.required()
    },
    {
      name: 'description',
      title: 'Description',
      type: 'text',
      description: 'Brief description of the year group',
      validation: Rule => Rule.required()
    },
    {
      name: 'keyStage',
      title: 'Key Stage',
      type: 'reference',
      description: 'The key stage this year group belongs to',
      to: [{type: 'keyStage'}],
      validation: Rule => Rule.required()
    },
    {
      name: 'lowerAgeBoundary',
      title: 'Lower Age Boundary',
      type: 'number',
      description: 'Minimum age for this year group',
      validation: Rule => Rule.required().min(0).integer()
    },
    {
      name: 'upperAgeBoundary',
      title: 'Upper Age Boundary',
      type: 'number',
      description: 'Maximum age for this year group',
      validation: Rule => Rule.required().positive().integer()
    }
  ],
  preview: {
    select: {
      title: 'label',
      keyStage: 'keyStage.label',
      lowerAge: 'lowerAgeBoundary',
      upperAge: 'upperAgeBoundary'
    },
    prepare({title, keyStage, lowerAge, upperAge}) {
      return {
        title,
        subtitle: `${keyStage} - Ages ${lowerAge}-${upperAge}`
      }
    }
  }
}
