<?php

declare(strict_types=1);

/**
 * SPDX-FileCopyrightText: 2024 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

namespace OCP\TaskProcessing\TaskTypes;

use OCP\IL10N;
use OCP\TaskProcessing\EShapeType;
use OCP\TaskProcessing\ITaskType;
use OCP\TaskProcessing\ShapeDescriptor;

/**
 * This is the task processing task type for text reformulation
 * @since 31.0.0
 */
class ContextAgentInteraction implements ITaskType {
	public const ID = 'core:contextagent:interaction';

	public function __construct(
		private IL10N $l,
	) {
	}

	/**
	 * @inheritDoc
	 */
	public function getName(): string {
		return $this->l->t('ContextAgent');
	}

	/**
	 * @inheritDoc
	 */
	public function getDescription(): string {
		return $this->l->t('Chat with an agent');
	}

	/**
	 * @return string
	 */
	public function getId(): string {
		return self::ID;
	}

	/**
	 * @return ShapeDescriptor[]
	 */
	public function getInputShape(): array {
		return [
			'input' => new ShapeDescriptor(
				$this->l->t('Chat message'),
				$this->l->t('A chat message to send to the agent.'),
				EShapeType::Text
			),
			'confirmation' => new ShapeDescriptor(
				$this->l->t('Confirmation'),
				$this->l->t('Whether to confirm previously requested actions: 0 for denial and 1 for confirmation.'),
				EShapeType::Number
			),
			'conversation_token' => new ShapeDescriptor(
				$this->l->t('Conversation token'),
				$this->l->t('A token representing the conversation.'),
				EShapeType::Text
			),
		];
	}

	/**
	 * @return ShapeDescriptor[]
	 */
	public function getOutputShape(): array {
		return [
			'output' => new ShapeDescriptor(
				$this->l->t('Generated response'),
				$this->l->t('The response from the chat model.'),
				EShapeType::Text
			),
			'conversation_token' => new ShapeDescriptor(
				$this->l->t('The new conversation token'),
				$this->l->t('Send this along with the next interaction.'),
				EShapeType::Text
			),
			'actions' => new ShapeDescriptor(
				$this->l->t('Requested actions by the agent'),
				$this->l->t('Actions that the agent would like to carry out in JSON format.'),
				EShapeType::Text
			),
		];
	}
}
