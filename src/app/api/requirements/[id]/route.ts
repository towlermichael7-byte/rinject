import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const data = await request.json()

    const requirement = await prisma.requirement.update({
      where: { id: params.id },
      data: {
        jobTitle: data.jobTitle,
        client: data.client,
        primeVendor: data.primeVendor,
        status: data.status,
        nextSteps: data.nextSteps,
        vendorInfo: data.vendorInfo,
        consultants: data.consultants,
        interviewId: data.interviewId
      }
    })

    return NextResponse.json(requirement)
  } catch (error) {
    console.error('Failed to update requirement:', error)
    return NextResponse.json(
      { error: 'Failed to update requirement' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await prisma.requirement.delete({
      where: { id: params.id }
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Failed to delete requirement:', error)
    return NextResponse.json(
      { error: 'Failed to delete requirement' },
      { status: 500 }
    )
  }
}