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
class TextToTextChatWithTools implements ITaskType {
	public const ID = 'core:text2text:chatwithtools';

	public function __construct(
		private IL10N $l,
	) {
	}

	/**
	 * @inheritDoc
	 */
	public function getName(): string {
		return $this->l->t('Chat with tools');
	}

	/**
	 * @inheritDoc
	 */
	public function getDescription(): string {
		return $this->l->t('Chat with the language model with tool calling support.');
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
			'system_prompt' => new ShapeDescriptor(
				$this->l->t('System prompt'),
				$this->l->t('Define rules and assumptions that the assistant should follow during the conversation.'),
				EShapeType::Text
			),
			'input' => new ShapeDescriptor(
				$this->l->t('Chat message'),
				$this->l->t('Describe a task that you want the assistant to do or ask a question'),
				EShapeType::Text
			),
			'history' => new ShapeDescriptor(
				$this->l->t('Chat history'),
				$this->l->t('The history of chat messages before the current message, starting with a message by the user'),
				EShapeType::ListOfTexts
			),
			// See https://platform.openai.com/docs/api-reference/chat/create#chat-create-tools for the format
			'tools' => new ShapeDescriptor(
				$this->l->t('Available tools'),
				$this->l->t('The available tools in JSON format'),
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
				$this->l->t('The response from the chat model'),
				EShapeType::Text
			),
			'tool_calls' => new ShapeDescriptor(
				$this->l->t('Tool calls'),
				$this->l->t('Tools call instructions from the model in JSON format'),
				EShapeType::Text
			),
		];
	}
}
