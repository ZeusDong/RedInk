<template>
  <Teleport to="body">
    <!-- Toast 通知 -->
    <Transition name="toast">
      <div v-if="toast.show" :class="['toast-notification', `toast-${toast.type}`]">
        <div class="toast-icon">
          <svg v-if="toast.type === 'success'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <svg v-else-if="toast.type === 'error'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
        </div>
        <span class="toast-message">{{ toast.message }}</span>
      </div>
    </Transition>

    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="handleClose(false)">
        <div class="confirm-modal">
          <!-- Header -->
          <header class="modal-header">
            <h2 class="modal-title">AI 分析确认</h2>
            <button class="close-btn" @click="handleClose(false)" title="关闭">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </header>

          <!-- Body -->
          <div class="modal-body">
            <!-- 修改警告横幅 -->
            <div v-if="modifiedFields.length > 0" class="modification-warning-banner">
              <div class="warning-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                  <line x1="12" y1="9" x2="12" y2="13"></line>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
              </div>
              <div class="warning-content">
                <div class="warning-title">⚠️ 检测到内容修改</div>
                <div class="warning-message">以下字段已从原始记录修改：{{ modifiedFields.map(f => f.fieldLabel).join('、') }}</div>
                <div class="warning-hint">修改后的内容将覆盖原始数据，请确认后再提交</div>
              </div>
            </div>
            <!-- 战略背景 -->
            <section class="form-section">
              <h3 class="section-title">【战略背景】</h3>

              <div class="form-group" :class="{ 'field-modified': isFieldModified('industry') }">
                <label class="form-label required">
                  所属赛道
                  <span v-if="isFieldModified('industry')" class="modified-badge">已修改</span>
                </label>
                <select v-model="formData.industry" class="form-select" :class="{ error: errors.industry }">
                  <option value="">请选择</option>
                  <option value="AI工具">AI工具</option>
                  <option value="职场搞钱">职场搞钱</option>
                  <option value="情感咨询">情感咨询</option>
                  <option value="美妆护肤">美妆护肤</option>
                  <option value="服饰穿搭">服饰穿搭</option>
                  <option value="美食">美食</option>
                  <option value="旅行">旅行</option>
                  <option value="家居">家居</option>
                  <option value="健身">健身</option>
                  <option value="教育">教育</option>
                  <option value="其他">其他</option>
                </select>
                <span v-if="errors.industry" class="form-error">{{ errors.industry }}</span>
              </div>

              <div class="form-row">
                <div class="form-group" :class="{ 'field-modified': isFieldModified('follower_count') }">
                  <label class="form-label required">
                    账号粉丝量
                    <span v-if="isFieldModified('follower_count')" class="modified-badge">已修改</span>
                  </label>
                  <input
                    v-model.number="formData.follower_count"
                    type="number"
                    min="0"
                    class="form-input"
                    :class="{ error: errors.follower_count }"
                    placeholder="0"
                  />
                  <span v-if="errors.follower_count" class="form-error">{{ errors.follower_count }}</span>
                </div>

                <div class="form-group" :class="{ 'field-modified': isFieldModified('published_at') }">
                  <label class="form-label">
                    发布时间
                    <span v-if="isFieldModified('published_at')" class="modified-badge">已修改</span>
                  </label>
                  <input
                    v-model="formData.published_at"
                    type="date"
                    class="form-input"
                  />
                </div>
              </div>

              <div class="form-group" :class="{ 'field-modified': isFieldModified('likes_count') || isFieldModified('saves_count') || isFieldModified('comments_count') }">
                <label class="form-label required">
                  数据表现
                  <span v-if="isFieldModified('likes_count') || isFieldModified('saves_count') || isFieldModified('comments_count')" class="modified-badge">已修改</span>
                </label>
                <div class="metrics-inputs">
                  <div class="metric-input">
                    <span class="metric-label">👍 点赞</span>
                    <input
                      v-model.number="formData.likes_count"
                      type="number"
                      min="0"
                      class="form-input"
                      :class="{ error: errors.likes_count }"
                    />
                  </div>
                  <div class="metric-input">
                    <span class="metric-label">💾 收藏</span>
                    <input
                      v-model.number="formData.saves_count"
                      type="number"
                      min="0"
                      class="form-input"
                      :class="{ error: errors.saves_count }"
                    />
                  </div>
                  <div class="metric-input">
                    <span class="metric-label">💬 评论</span>
                    <input
                      v-model.number="formData.comments_count"
                      type="number"
                      min="0"
                      class="form-input"
                      :class="{ error: errors.comments_count }"
                    />
                  </div>
                </div>
                <span v-if="errors.metrics" class="form-error">{{ errors.metrics }}</span>
              </div>
            </section>

            <!-- 内容本体 -->
            <section class="form-section">
              <h3 class="section-title">【内容本体】</h3>

              <div class="form-group" :class="{ 'field-modified': isFieldModified('title') }">
                <label class="form-label required">
                  标题/封面文案
                  <span v-if="isFieldModified('title')" class="modified-badge">已修改</span>
                </label>
                <input
                  v-model="formData.title"
                  type="text"
                  class="form-input"
                  :class="{ error: errors.title }"
                  placeholder="请输入标题"
                  maxlength="100"
                />
                <span class="char-count">{{ formData.title.length }}/100</span>
                <span v-if="errors.title" class="form-error">{{ errors.title }}</span>
              </div>

              <div class="form-group" :class="{ 'field-modified': isFieldModified('content') }">
                <label class="form-label required">
                  正文/脚本全文
                  <span v-if="isFieldModified('content')" class="modified-badge">已修改</span>
                </label>
                <textarea
                  v-model="formData.content"
                  class="form-textarea"
                  :class="{ error: errors.content }"
                  placeholder="请输入正文内容..."
                  rows="6"
                ></textarea>
                <span v-if="errors.content" class="form-error">{{ errors.content }}</span>
              </div>
            </section>

            <!-- 视觉与互动 -->
            <section class="form-section">
              <h3 class="section-title">【视觉与互动】</h3>

              <!-- 图片选择区域 -->
              <div v-if="hasImages" class="image-selection-area">
                <!-- 封面图 -->
                <div class="image-group cover-group">
                  <label class="group-label">【封面图】</label>
                  <div class="image-checkbox" :class="{ checked: coverSelected, error: coverLoadError }">
                    <!-- Badge for cover image (index -1) -->
                    <span
                      v-if="getBadgeState(-1) !== 'none'"
                      class="image-badge"
                      :class="getBadgeState(-1)"
                      :title="getBadgeTitle(getBadgeState(-1))"
                    >
                      {{ getBadgeIcon(getBadgeState(-1)) }}
                    </span>

                    <input type="checkbox" v-model="coverSelected" />
                    <img
                      v-if="record?.cover_image"
                      :src="record.cover_image"
                      @error="handleCoverError"
                      alt="封面图"
                    />
                    <div v-else class="image-placeholder">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <circle cx="8.5" cy="8.5" r="1.5"></circle>
                        <polyline points="21 15 16 10 5 21"></polyline>
                      </svg>
                    </div>
                    <span v-if="coverLoadError" class="load-error-icon" title="图片加载失败">⚠️</span>
                  </div>
                </div>

                <!-- 内容图 -->
                <div v-if="record?.images?.length" class="image-group content-group">
                  <label class="group-label">【内容图】({{ record.images.length }}张)</label>
                  <div class="content-images-grid">
                    <div
                      v-for="(img, idx) in record.images"
                      :key="idx"
                      class="image-checkbox"
                      :class="{ checked: isContentImageSelected(idx), error: contentLoadErrors.has(idx) }"
                    >
                      <!-- Badge for content image -->
                      <span
                        v-if="getBadgeState(idx) !== 'none'"
                        class="image-badge"
                        :class="getBadgeState(idx)"
                        :title="getBadgeTitle(getBadgeState(idx))"
                      >
                        {{ getBadgeIcon(getBadgeState(idx)) }}
                      </span>
                      <input
                        type="checkbox"
                        :checked="isContentImageSelected(idx)"
                        @change="toggleContentImage(idx)"
                      />
                      <img
                        v-if="!contentLoadErrors.has(idx)"
                        :src="img"
                        @error="() => handleContentError(idx)"
                        :alt="`内容图${idx + 1}`"
                      />
                      <div v-else class="image-error-placeholder" :title="img">
                        <span class="error-text">加载失败</span>
                      </div>
                      <span class="image-label">图{{ idx + 1 }}</span>
                      <span v-if="contentLoadErrors.has(idx)" class="load-error-icon" title="图片加载失败">⚠️</span>
                    </div>
                  </div>
                  <div class="quick-actions">
                    <button type="button" @click="selectAllContent">全选</button>
                    <button type="button" @click="clearAllContent">清空选择</button>
                  </div>
                </div>
              </div>

              <!-- 无图片提示 -->
              <div v-else class="no-images-message">
                <p>⚠️ 暂无可用图片</p>
                <p>该笔记没有封面图或内容图，请手动输入视觉描述</p>
              </div>

              <!-- 操作栏 -->
              <div v-if="hasImages" class="visual-action-bar">
                <div class="action-left">
                  <span class="selection-count">已选择 {{ selectedCount }} 张图片</span>
                  <!-- 追加/覆盖模式切换 -->
                  <div class="mode-toggle" v-if="formData.visual_description">
                    <button
                      type="button"
                      class="mode-btn"
                      :class="{ active: visualDescMode === 'append' }"
                      @click="visualDescMode = 'append'"
                      title="新生成的描述将追加到现有描述后面"
                    >
                      追加
                    </button>
                    <button
                      type="button"
                      class="mode-btn"
                      :class="{ active: visualDescMode === 'replace' }"
                      @click="visualDescMode = 'replace'"
                      title="新生成的描述将替换现有描述"
                    >
                      覆盖
                    </button>
                  </div>
                </div>
                <button
                  type="button"
                  class="btn-generate"
                  @click="handleGenerateVisualDesc"
                  :disabled="selectedCount === 0 || generatingVisual"
                >
                  <svg v-if="!generatingVisual" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                  </svg>
                  {{ generatingVisual ? '生成中...' : '生成视觉描述' }}
                </button>
              </div>

              <!-- 视觉描述 - 卡片式 -->
              <div class="form-group" :class="{ 'field-modified': isFieldModified('visual_description') }">
                <label class="form-label required">
                  视觉描述
                  <span v-if="isFieldModified('visual_description')" class="modified-badge">已修改</span>
                </label>

                <!-- 卡片列表 -->
                <div v-if="parsedImageDescriptions.length > 0" class="image-desc-cards">
                  <div
                    v-for="item in parsedImageDescriptions"
                    :key="item.id"
                    class="image-desc-card"
                    :class="{ 'card-error': errors.visual_description && !item.content.trim() }"
                  >
                    <!-- 卡片头部 -->
                    <div class="card-header">
                      <div class="card-title">
                        <!-- 缩略图 -->
                        <img
                          v-if="item.imageSrc"
                          :src="item.imageSrc"
                          class="card-thumb"
                          :alt="item.label"
                        />
                        <div v-else class="card-thumb-placeholder">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                            <circle cx="8.5" cy="8.5" r="1.5"></circle>
                            <polyline points="21 15 16 10 5 21"></polyline>
                          </svg>
                        </div>
                        <span class="card-label">{{ item.label }}</span>
                        <!-- 状态标识 -->
                        <span
                          v-if="getBadgeState(item.index) !== 'none'"
                          class="card-badge"
                          :class="getBadgeState(item.index)"
                          :title="getBadgeTitle(getBadgeState(item.index))"
                        >
                          {{ getBadgeIcon(getBadgeState(item.index)) }}
                        </span>
                      </div>
                      <button
                        type="button"
                        class="card-delete-btn"
                        @click="removeImageDescription(item.id)"
                        title="删除此描述"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <line x1="18" y1="6" x2="6" y2="18"></line>
                          <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                      </button>
                    </div>

                    <!-- 卡片内容 - 可编辑描述 -->
                    <textarea
                      :value="item.content"
                      @input="updateImageDescription(item.id, $event)"
                      class="card-textarea"
                      placeholder="描述此图片的视觉风格、配色、构图等..."
                      rows="3"
                    >{{ item.content }}</textarea>
                  </div>
                </div>

                <!-- 空状态提示 -->
                <div v-else class="empty-cards-hint">
                  <p v-if="hasImages">
                    <span>👆 选择图片后点击「生成视觉描述」，或</span>
                    <button type="button" class="manual-add-btn" @click="handleAddManualDescription">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                      </svg>
                      手动添加描述
                    </button>
                  </p>
                  <p v-else>
                    <span>请描述图片的视觉风格、配色、构图等...</span>
                    <button type="button" class="manual-add-btn" @click="handleAddManualDescription">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                      </svg>
                      手动添加描述
                    </button>
                  </p>
                </div>

                <!-- 添加手动描述按钮（有卡片时也显示） -->
                <div v-if="parsedImageDescriptions.length > 0" class="add-manual-desc-wrapper">
                  <button type="button" class="add-manual-desc-btn" @click="handleAddManualDescription">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    添加描述
                  </button>
                  <span class="add-desc-hint">可随时手动添加或编辑描述</span>
                </div>

                <!-- 错误提示 -->
                <span v-if="errors.visual_description" class="form-error">{{ errors.visual_description }}</span>
              </div>

              <div class="form-group" :class="{ 'field-modified': isFieldModified('top_comments') }">
                <label class="form-label">
                  高赞评论
                  <span v-if="isFieldModified('top_comments')" class="modified-badge">已修改</span>
                </label>
                <div class="comments-list">
                  <!-- Main comments -->
                  <div v-for="(comment, commentIndex) in formData.top_comments" :key="comment.id" class="comment-card">
                    <!-- Main comment header -->
                    <div class="comment-card-header">
                      <span class="comment-number">评论 {{ commentIndex + 1 }}</span>
                      <button
                        type="button"
                        class="remove-comment-btn"
                        @click="removeComment(commentIndex)"
                        title="删除评论"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <line x1="18" y1="6" x2="6" y2="18"></line>
                          <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                      </button>
                    </div>

                    <!-- Main comment content -->
                    <div class="comment-content">
                      <textarea
                        v-model="comment.content"
                        class="form-textarea comment-textarea"
                        placeholder="输入评论内容..."
                        rows="3"
                      ></textarea>
                    </div>

                    <!-- Main comment footer -->
                    <div class="comment-footer">
                      <button
                        type="button"
                        class="add-sub-comment-btn"
                        @click="addSubComment(commentIndex)"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <line x1="12" y1="5" x2="12" y2="19"></line>
                          <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        添加回复
                      </button>
                      <div class="likes-wrapper">
                        <label class="likes-label">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                          </svg>
                          <input
                            v-model.number="comment.likes"
                            type="number"
                            class="likes-input"
                            placeholder="赞数"
                            min="0"
                          />
                        </label>
                      </div>
                    </div>

                    <!-- Sub-comments -->
                    <div v-if="comment.sub_comments && comment.sub_comments.length > 0" class="sub-comments-section">
                      <div class="sub-comments-header">
                        <span class="sub-comments-title">回复 ({{ comment.sub_comments.length }})</span>
                      </div>
                      <div class="sub-comments-grid">
                        <div
                          v-for="(subComment, subIndex) in comment.sub_comments"
                          :key="subComment.id"
                          class="sub-comment-card"
                        >
                          <div class="sub-comment-header">
                            <label class="blogger-toggle" :class="{ active: subComment.is_blogger }">
                              <input type="checkbox" v-model="subComment.is_blogger" />
                              <span class="toggle-indicator"></span>
                              <span class="toggle-label">博主</span>
                            </label>
                            <button
                              type="button"
                              class="remove-sub-comment-btn"
                              @click="removeSubComment(commentIndex, subIndex)"
                              title="删除回复"
                            >
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                              </svg>
                            </button>
                          </div>
                          <textarea
                            v-model="subComment.content"
                            class="form-textarea sub-comment-textarea"
                            placeholder="输入回复内容..."
                            rows="2"
                          ></textarea>
                          <div class="sub-comment-footer">
                            <label class="mini-likes">
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                              </svg>
                              <input
                                v-model.number="subComment.likes"
                                type="number"
                                placeholder="0"
                                min="0"
                              />
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Add main comment button -->
                  <button type="button" class="add-comment-btn" @click="addComment">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    添加评论
                  </button>
                </div>
              </div>
            </section>
          </div>

          <!-- Footer -->
          <footer class="modal-footer">
            <button class="btn btn-secondary" @click="handleSaveDraft" :disabled="saving">
              {{ saving ? '保存中...' : '保存草稿' }}
            </button>
            <button class="btn btn-primary" @click="handleSubmit" :disabled="submitting">
              <svg v-if="!submitting" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
              </svg>
              <span v-if="progressMessage" class="progress-message">{{ progressMessage }}</span>
              <span v-else class="button-text">{{ submitting ? '分析中...' : '开始 AI 分析' }}</span>
            </button>
          </footer>
        </div>
      </div>
    </Transition>

    <!-- 图片选择弹窗 -->
    <Transition name="modal">
      <div v-if="showImageSelector" class="modal-overlay" @click.self="closeImageSelector">
        <div class="image-selector-modal">
          <!-- Header -->
          <header class="selector-header">
            <h3 class="selector-title">选择要描述的图片</h3>
            <button class="close-btn" @click="closeImageSelector" title="关闭">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </header>

          <!-- Body -->
          <div class="selector-body">
            <p class="selector-hint">点击图片卡片选择要添加视觉描述的图片</p>

            <!-- 图片网格 -->
            <div class="selector-image-grid">
              <div
                v-for="item in availableImages"
                :key="item.index"
                class="selector-image-card"
                :class="{ selected: selectedImageIndex === item.index, 'has-desc': item.hasDesc }"
                @click="selectedImageIndex = item.index"
              >
                <!-- 图片缩略图 -->
                <div class="selector-thumb-wrapper">
                  <img
                    v-if="item.imageSrc"
                    :src="item.imageSrc"
                    class="selector-thumb"
                    :alt="item.label"
                  />
                  <div v-else class="selector-thumb-placeholder">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                      <circle cx="8.5" cy="8.5" r="1.5"></circle>
                      <polyline points="21 15 16 10 5 21"></polyline>
                    </svg>
                  </div>
                  <!-- 选中标记 -->
                  <span v-if="selectedImageIndex === item.index" class="selector-selected-badge">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"></path>
                    </svg>
                  </span>
                </div>

                <!-- 图片标签 -->
                <div class="selector-label">{{ item.label }}</div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <footer class="selector-footer">
            <button class="btn btn-secondary" @click="closeImageSelector">
              取消
            </button>
            <button class="btn btn-primary" @click="confirmImageSelection" :disabled="selectedImageIndex === null">
              确认添加
            </button>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, computed } from 'vue'
import type { ReferenceRecord } from '@/api'
import { useImageDescriptionBadge } from '@/composables/useImageDescriptionBadge'
import type { ImageDescription, Comment, SubComment } from '@/types/analysis'
import { useAnalysisStore } from '@/stores/analysis'

interface Props {
  visible: boolean
  record: ReferenceRecord | null
}

interface Emits {
  (e: 'close'): void
  (e: 'save-draft', data: any): void
  (e: 'submit', data: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 获取分析 store
const analysisStore = useAnalysisStore()

// 表单数据
const formData = reactive({
  record_id: '',
  industry: '',
  follower_count: 0,
  published_at: '',
  likes_count: 0,
  saves_count: 0,
  comments_count: 0,
  title: '',
  content: '',
  visual_description: '',
  top_comments: [] as Comment[]
})

// 验证错误
const errors = reactive<Record<string, string>>({})

// 状态
const saving = ref(false)
const submitting = ref(false)
const generatingVisual = ref(false)
// 进度步骤：用于显示 AI 分析的当前步骤
const progressStep = ref<string>('')
const progressMessage = ref<string>('')

// Toast 通知状态
const toast = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

// 显示 Toast 通知
function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  // 3秒后自动消失
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

// ========== 新增：图片选择器状态 ==========
const showImageSelector = ref(false)
const selectedImageIndex = ref<number | null>(null)

// 可用图片列表（计算属性）
const availableImages = computed<Array<{
  index: number
  label: string
  hasDesc: boolean
  imageSrc?: string
}>>(() => {
  if (!props.record) return []

  const result: Array<{ index: number; label: string; hasDesc: boolean; imageSrc?: string }> = []

  // 封面图
  if (props.record.cover_image) {
    result.push({
      index: -1,
      label: '封面图',
      hasDesc: imageDescriptions.value[-1] !== undefined,
      imageSrc: props.record.cover_image
    })
  }

  // 内容图
  if (props.record.images && props.record.images.length > 0) {
    for (let i = 0; i < props.record.images.length; i++) {
      result.push({
        index: i,
        label: `内容图${i + 1}`,
        hasDesc: imageDescriptions.value[i] !== undefined,
        imageSrc: props.record.images[i]
      })
    }
  }

  return result
})

// 追踪是否有未保存的修改
const hasUnsavedChanges = ref(false)

// 标记是否正在加载数据（避免加载期间触发未保存标记）
const isLoading = ref(false)

// 存储初始化完成时的表单数据快照（用于比较是否真的有变化）
const initialFormDataSnapshot = ref<string>('')

// 存储原始记录数据（用于字段级别的比较）
const originalRecordData = ref<{
  record_id: string
  title: string
  content: string
  industry: string
  follower_count: number
  published_at: string
  likes_count: number
  saves_count: number
  comments_count: number
  visual_description: string
  top_comments: Comment[]
}>({
  record_id: '',
  title: '',
  content: '',
  industry: '',
  follower_count: 0,
  published_at: '',
  likes_count: 0,
  saves_count: 0,
  comments_count: 0,
  visual_description: '',
  top_comments: []
})

// 字段级别的变化追踪
interface FieldChange {
  fieldName: string
  fieldLabel: string
  originalValue: any
  currentValue: any
  hasChanged: boolean
}

const fieldChanges = ref<Record<string, FieldChange>>({})

// 获取已修改的字段列表
const modifiedFields = computed(() => {
  return Object.values(fieldChanges.value).filter(f => f.hasChanged)
})

// 检查字段是否被修改
function isFieldModified(fieldName: string): boolean {
  return fieldChanges.value[fieldName]?.hasChanged || false
}

// 更新字段变化状态
function updateFieldChanges() {
  if (!originalRecordData.value.title && !isLoading.value) return

  const fields: Array<{ key: keyof typeof formData, label: string }> = [
    { key: 'title', label: '标题' },
    { key: 'content', label: '正文' },
    { key: 'industry', label: '所属赛道' },
    { key: 'follower_count', label: '粉丝量' },
    { key: 'published_at', label: '发布时间' },
    { key: 'likes_count', label: '点赞数' },
    { key: 'saves_count', label: '收藏数' },
    { key: 'comments_count', label: '评论数' },
    { key: 'visual_description', label: '视觉描述' }
  ]

  fields.forEach(({ key, label }) => {
    const original = originalRecordData.value[key]
    const current = formData[key]
    const hasChanged = JSON.stringify(original) !== JSON.stringify(current)

    fieldChanges.value[key] = {
      fieldName: key,
      fieldLabel: label,
      originalValue: original,
      currentValue: current,
      hasChanged
    }
  })

  // 特殊处理评论（因为结构复杂）
  const originalComments = JSON.stringify(originalRecordData.value.top_comments)
  const currentComments = JSON.stringify(formData.top_comments)
  fieldChanges.value['top_comments'] = {
    fieldName: 'top_comments',
    fieldLabel: '高赞评论',
    originalValue: originalRecordData.value.top_comments,
    currentValue: formData.top_comments,
    hasChanged: originalComments !== currentComments
  }
}

// 视觉描述生成模式：'append'（追加）或 'replace'（覆盖）
const visualDescMode = ref<'append' | 'replace'>('append')

// ========== 新增：图片选择状态 ==========

// 选中的图片索引（-1=封面，0+=内容图）
const selectedImageIndices = ref<number[]>([-1])  // 默认选中封面

// 图片加载错误状态
const coverLoadError = ref(false)
const contentLoadErrors = ref<Set<number>>(new Set())

// 本地图片检查状态
const hasCheckedLocal = ref(false)

// ========== 新增：卡片式视觉描述 ==========

// 图片描述卡片类型
interface ImageDescCard {
  id: string          // 唯一ID
  index: number       // 图片索引（-1=封面，0+=内容图）
  label: string       // 显示标签（如"封面图"、"内容图1"）
  content: string     // 描述内容
  imageSrc?: string   // 图片URL
}

// 解析视觉描述字符串为卡片数组
const parsedImageDescriptions = computed<ImageDescCard[]>(() => {
  const result: ImageDescCard[] = []
  const desc = formData.visual_description.trim()

  console.log('[parsedImageDescriptions] Input visual_description:', desc)
  console.log('[parsedImageDescriptions] Input length:', desc.length)
  console.log('[parsedImageDescriptions] imageDescriptions metadata:', imageDescriptions.value)

  if (!desc) {
    console.log('[parsedImageDescriptions] Empty input, returning empty array')
    return result
  }

  // Normalize line endings for consistent parsing
  const normalizedDesc = desc.replace(/\r\n/g, '\n').replace(/\r/g, '\n')

  console.log('[parsedImageDescriptions] Normalized desc:', normalizedDesc.slice(0, 500))

  // 更宽松的匹配模式：逐步匹配，然后按行分割
  // 1. 首先找到所有 <!-- DESC-xxx --> 标记
  // 2. 然后提取标记后的内容（标签+内容）

  const markerPattern = /<!--\s*DESC-([a-z0-9-]+)\s*-->/gi
  const markers: Array<{match: string, id: string, index: number}> = []

  let markerMatch: RegExpExecArray | null
  while ((markerMatch = markerPattern.exec(normalizedDesc)) !== null) {
    markers.push({
      match: markerMatch[0],
      id: markerMatch[1],
      index: markerMatch.index
    })
  }

  console.log('[parsedImageDescriptions] Found markers:', markers.length)

  // 为每个标记提取内容
  for (let i = 0; i < markers.length; i++) {
    const { id, index: markerIndex } = markers[i]

    // 内容从标记后开始
    const contentStart = markerIndex + markers[i].match.length

    // 找到下一个标记或字符串末尾
    let contentEnd = normalizedDesc.length
    if (i < markers.length - 1) {
      contentEnd = markers[i + 1].index
    }

    // 提取原始内容
    let rawContent = normalizedDesc.substring(contentStart, contentEnd).trim()

    console.log(`[parsedImageDescriptions] Processing marker ${i + 1}/${markers.length}:`, {
      id,
      rawContentLength: rawContent.length,
      rawContentPreview: rawContent.slice(0, 200)
    })

    // 按行分割，第一行是标签，其余是内容
    const lines = rawContent.split('\n')
    let label = ''
    let content = ''

    if (lines.length >= 2) {
      label = lines[0].trim()
      content = lines.slice(1).join('\n').trim()
    } else if (lines.length === 1) {
      // 只有一行，可能是标签，内容为空
      label = lines[0].trim()
      content = ''
    }

    // 从 ID 中提取索引（最后一部分是索引，如 "0", "1", "-1"）
    // 注意：封面图的 ID 格式可能是 xxx-xxx--1，需要特殊处理
    let index = 0
    if (id.endsWith('--1')) {
      index = -1
    } else {
      const lastDashIndex = id.lastIndexOf('-')
      if (lastDashIndex !== -1) {
        index = parseInt(id.substring(lastDashIndex + 1), 10)
      }
    }

    console.log(`[parsedImageDescriptions] Parsed:`, {
      id,
      index,
      label,
      contentLength: content.length,
      contentPreview: content.slice(0, 100)
    })

    // 优先使用 imageDescriptions 中的数据（更可靠）
    // 如果 visual_description 中没有内容，从元数据中获取
    let finalContent = content
    let finalLabel = label

    // 在 imageDescriptions 中查找匹配的描述
    // 通过 id 或 index 匹配
    const metaDesc = Object.values(imageDescriptions.value).find(d => d.id === id) || (imageDescriptions.value as Record<string, ImageDescription>)[String(index)]

    if (metaDesc) {
      console.log(`[parsedImageDescriptions] Found metadata for ${id}, using metadata content`)
      // 如果元数据中有内容，优先使用
      if (metaDesc.content) {
        finalContent = metaDesc.content
      }
      // 如果解析出的标签为空，从元数据中推断
      if (!finalLabel) {
        const metaIndex = Object.keys(imageDescriptions.value).find(k => (imageDescriptions.value as Record<string, ImageDescription>)[k]?.id === id)
        if (metaIndex) {
          const idx = parseInt(metaIndex, 10)
          finalLabel = idx === -1 ? '【封面图】' : `【内容图${idx + 1}】`
        }
      }
    }

    console.log(`[parsedImageDescriptions] Final:`, {
      id,
      index,
      finalLabel,
      finalContentLength: finalContent.length,
      finalContentPreview: finalContent.slice(0, 100)
    })

    // 获取图片URL
    let imageSrc: string | undefined
    if (index === -1) {
      imageSrc = props.record?.cover_image
    } else if (props.record?.images && index >= 0 && index < props.record.images.length) {
      imageSrc = props.record.images[index]
    }

    result.push({
      id,
      index,
      label: finalLabel,
      content: finalContent,
      imageSrc
    })
  }

  console.log('[parsedImageDescriptions] Total cards created:', result.length)
  console.log('[parsedImageDescriptions] Final result array:', result.map(r => ({
    id: r.id,
    label: r.label,
    contentLength: r.content.length,
    contentPreview: r.content.slice(0, 50)
  })))

  return result
})

// 更新单张图片的描述内容
function updateImageDescription(id: string, event: Event) {
  const target = event.target as HTMLTextAreaElement
  const newContent = target.value

  // 找到对应的卡片
  const card = parsedImageDescriptions.value.find(c => c.id === id)
  if (!card) return

  // 重新构建 visual_description 字符串
  rebuildVisualDescription(id, newContent)
}

// 重新构建视觉描述字符串
function rebuildVisualDescription(changedId?: string, newContent?: string, excludeId?: string) {
  let cards = parsedImageDescriptions.value.map(c => {
    // 如果是更新的卡片，使用新内容
    if (changedId && c.id === changedId) {
      return { ...c, content: newContent || '' }
    }
    return c
  })

  // 过滤掉被删除的卡片
  if (excludeId) {
    cards = cards.filter(c => c.id !== excludeId)
  }

  // 重建字符串
  if (cards.length === 0) {
    formData.visual_description = ''
    return
  }

  const newDesc = cards.map(c => {
    return `<!-- DESC-${c.id} -->\n${c.label}\n${c.content}`
  }).join('\n\n---\n\n')

  formData.visual_description = newDesc
}

// 删除单张图片的描述
function removeImageDescription(id: string) {
  if (!confirm('确定要删除此描述吗？')) return

  // 从 imageDescriptions 元数据中移除
  const card = parsedImageDescriptions.value.find(c => c.id === id)
  if (card) {
    delete imageDescriptions.value[card.index]
  }

  // 重建字符串（排除被删除的卡片）
  rebuildVisualDescription(undefined, undefined, id)
}

// ========== 新增：图片描述元数据 ==========

// Image description metadata per image index
const imageDescriptions = ref<Record<number, ImageDescription>>({})

// Use the badge composable
// Need to pass a computed getter to maintain reactivity since formData.visual_description is a plain string
const visualDescGetter = computed(() => formData.visual_description)

const {
  getBadgeState,
  getBadgeIcon,
  getBadgeTitle
} = useImageDescriptionBadge({
  imageDescriptions,
  visualDescription: visualDescGetter  // Pass computed ref that tracks changes to formData.visual_description
})

// ========== 新增：计算属性 ==========

// 是否有可用图片
const hasImages = computed(() => {
  return !!(props.record?.cover_image || (props.record?.images && props.record.images.length > 0))
})

// 已选中图片数量
const selectedCount = computed(() => {
  return selectedImageIndices.value.length
})

// 封面图是否选中（双向绑定computed）
const coverSelected = computed({
  get: () => selectedImageIndices.value.includes(-1),
  set: (val: boolean) => {
    if (val && !selectedImageIndices.value.includes(-1)) {
      selectedImageIndices.value.push(-1)
    } else if (!val) {
      selectedImageIndices.value = selectedImageIndices.value.filter(i => i !== -1)
    }
  }
})

// 初始化表单数据
onMounted(() => {
  checkLocalImages()
  loadDraftOrRecord()
})

// 监听 record 变化
watch(() => props.record, (newRecord) => {
  if (newRecord) {
    // Debug: 打印图片信息
    console.log('[AnalyzeConfirmModal] Record changed, images count:', newRecord.images?.length || 0)
    console.log('[AnalyzeConfirmModal] Image URLs:', newRecord.images)
    console.log('[AnalyzeConfirmModal] Cover image:', newRecord.cover_image)
    // 重置本地检查状态并检查本地图片
    hasCheckedLocal.value = false
    checkLocalImages()
    loadDraftOrRecord()
  }
})

// 监听 visible 变化
watch(() => props.visible, (visible) => {
  if (visible) {
    loadDraftOrRecord()
  }
})

// Debug: 监听 visual_description 变化
watch(() => formData.visual_description, (newVal, oldVal) => {
  console.log('[AnalyzeConfirmModal] visual_description changed:')
  console.log('  Old length:', oldVal?.length || 0)
  console.log('  New length:', newVal?.length || 0)
  console.log('  New value preview:', newVal?.slice(0, 200) + (newVal?.length > 200 ? '...' : ''))
}, { immediate: true })

// 监听表单数据变化，标记为未保存
watch(formData, () => {
  // Skip if this is the initial load (record hasn't been loaded yet)
  if (!formData.record_id) return
  // Skip if currently loading data
  if (isLoading.value) return
  // Skip if no snapshot yet (not initialized)
  if (!initialFormDataSnapshot.value) return

  // Compare with initial snapshot to detect real changes
  const currentSnapshot = JSON.stringify({
    record_id: formData.record_id,
    industry: formData.industry,
    follower_count: formData.follower_count,
    published_at: formData.published_at,
    likes_count: formData.likes_count,
    saves_count: formData.saves_count,
    comments_count: formData.comments_count,
    title: formData.title,
    content: formData.content,
    visual_description: formData.visual_description,
    top_comments: formData.top_comments
  })

  hasUnsavedChanges.value = (currentSnapshot !== initialFormDataSnapshot.value)

  // Update field-level change tracking
  updateFieldChanges()
}, { deep: true })

async function loadDraftOrRecord() {
  if (!props.record) return

  isLoading.value = true
  // IMPORTANT: Reset hasUnsavedChanges BEFORE any data modifications
  // This ensures that even if watch is triggered during async operations, it will be overridden
  hasUnsavedChanges.value = false
  try {
    // 先尝试加载草稿
    try {
      const response = await fetch(`/api/analysis/draft?record_id=${props.record.record_id}`)
      const result = await response.json()

      if (result.success && result.data) {
        // Debug: 打印草稿数据
        console.log('[AnalyzeConfirmModal] Loading draft data:', result.data)
        console.log('[AnalyzeConfirmModal] Draft visual_description:', result.data.visual_description)
        console.log('[AnalyzeConfirmModal] Draft image_descriptions:', result.data.image_descriptions)

        // 加载草稿数据
        Object.assign(formData, {
          record_id: result.data.record_id || props.record.record_id,
          industry: result.data.industry || '',
          follower_count: result.data.follower_count || 0,
          published_at: result.data.published_at ? result.data.published_at.split('T')[0] : '',
          likes_count: result.data.likes_count || 0,
          saves_count: result.data.saves_count || 0,
          comments_count: result.data.comments_count || 0,
          title: result.data.title || '',
          content: result.data.content || '',
          visual_description: result.data.visual_description || '',
          top_comments: migrateTopComments(result.data.top_comments || [])
        })

        // Load image descriptions from draft
        if (result.data.image_descriptions) {
          imageDescriptions.value = result.data.image_descriptions
        } else {
          imageDescriptions.value = {}
        }

        // Fix: 如果 visual_description 为空但 image_descriptions 有内容，则重建 visual_description
        if (!formData.visual_description.trim() && Object.keys(imageDescriptions.value).length > 0) {
          console.log('[AnalyzeConfirmModal] Reconstructing visual_description from image_descriptions metadata')
          const reconstructedParts: string[] = []

          // 按 index 顺序重建 (-1 优先，然后 0, 1, 2...)
          const sortedIndices = Object.keys(imageDescriptions.value)
            .map(k => parseInt(k, 10))
            .sort((a, b) => {
              // -1 (封面) 排在最前面
              if (a === -1) return -1
              if (b === -1) return 1
              return a - b
            })

          for (const idx of sortedIndices) {
            const desc = imageDescriptions.value[idx]
            if (!desc) continue

            // 生成标签
            const label = idx === -1 ? '【封面图】' : `【内容图${idx + 1}】`

            // 格式: <!-- DESC-${uniqueId} -->\n${label}\n${content}
            reconstructedParts.push(`<!-- DESC-${desc.id} -->\n${label}\n${desc.content}`)
          }

          formData.visual_description = reconstructedParts.join('\n\n---\n\n')
          console.log('[AnalyzeConfirmModal] Reconstructed visual_description:', formData.visual_description.slice(0, 200) + '...')
        }

        console.log('[AnalyzeConfirmModal] Loaded formData.visual_description:', formData.visual_description)
        console.log('[AnalyzeConfirmModal] Loaded imageDescriptions:', imageDescriptions.value)

        // Save snapshot after loading draft
        initialFormDataSnapshot.value = JSON.stringify({
          record_id: formData.record_id,
          industry: formData.industry,
          follower_count: formData.follower_count,
          published_at: formData.published_at,
          likes_count: formData.likes_count,
          saves_count: formData.saves_count,
          comments_count: formData.comments_count,
          title: formData.title,
          content: formData.content,
          visual_description: formData.visual_description,
          top_comments: formData.top_comments
        })

        // Store original data for field-level comparison
        // For drafts, treat the draft as the original
        originalRecordData.value = {
          record_id: formData.record_id,
          title: formData.title,
          content: formData.content,
          industry: formData.industry,
          follower_count: formData.follower_count,
          published_at: formData.published_at,
          likes_count: formData.likes_count,
          saves_count: formData.saves_count,
          comments_count: formData.comments_count,
          visual_description: formData.visual_description,
          top_comments: JSON.parse(JSON.stringify(formData.top_comments))
        }
        fieldChanges.value = {}  // Reset field changes after loading draft

        // Reset unsaved flag after loading draft
        hasUnsavedChanges.value = false
        // Set isLoading to false AFTER resetting hasUnsavedChanges to avoid race condition
        isLoading.value = false
        return
      }
    } catch (e) {
      console.error('[AnalyzeConfirmModal] Failed to load draft:', e)
    }

    // 从 record 加载数据
    formData.record_id = props.record.record_id
    // Clear image descriptions when loading from record (not draft)
    imageDescriptions.value = {}
    formData.industry = props.record.industry || ''
    formData.follower_count = props.record.blogger?.follower_count || 0
    formData.published_at = props.record.created_at ? props.record.created_at.split('T')[0] : ''
    formData.likes_count = props.record.metrics?.likes || 0
    formData.saves_count = props.record.metrics?.saves || 0
    formData.comments_count = props.record.metrics?.comments || 0
    formData.title = props.record.title || ''
    formData.content = props.record.body || ''
    formData.visual_description = ''
    formData.top_comments = migrateTopComments([])

    // Save snapshot after loading from record
    initialFormDataSnapshot.value = JSON.stringify({
      record_id: formData.record_id,
      industry: formData.industry,
      follower_count: formData.follower_count,
      published_at: formData.published_at,
      likes_count: formData.likes_count,
      saves_count: formData.saves_count,
      comments_count: formData.comments_count,
      title: formData.title,
      content: formData.content,
      visual_description: formData.visual_description,
      top_comments: formData.top_comments
    })

    // Store original data for field-level comparison when loading from record
    originalRecordData.value = {
      record_id: formData.record_id,
      title: formData.title,
      content: formData.content,
      industry: formData.industry,
      follower_count: formData.follower_count,
      published_at: formData.published_at,
      likes_count: formData.likes_count,
      saves_count: formData.saves_count,
      comments_count: formData.comments_count,
      visual_description: formData.visual_description,
      top_comments: JSON.parse(JSON.stringify(formData.top_comments))
    }
    fieldChanges.value = {}  // Reset field changes after loading from record

    // Reset unsaved flag after loading from record
    hasUnsavedChanges.value = false
    // Set isLoading to false AFTER resetting hasUnsavedChanges to avoid race condition
    isLoading.value = false
  } catch (e) {
    // Only set isLoading to false in catch block
    isLoading.value = false
  }
}

// ========== Migration Helper ==========
/**
 * Migrate old string[] format to new Comment[] format
 * @param comments - Comments from API (either string[] or Comment[])
 */
function migrateTopComments(comments: string[] | Comment[]): Comment[] {
  if (!comments || comments.length === 0) {
    return []
  }

  // Check if already in new format (first item has 'content' property)
  if (typeof comments[0] === 'object' && 'content' in comments[0]) {
    return comments as Comment[]
  }

  // Old format: string[] -> migrate to Comment[]
  return (comments as string[]).map((content: string) => ({
    id: generateId(),
    content,
    likes: undefined,
    sub_comments: []
  }))
}

function validate(): boolean {
  // 清空错误
  Object.keys(errors).forEach(key => delete errors[key])

  let isValid = true

  if (!formData.industry) {
    errors.industry = '请选择所属赛道'
    isValid = false
  }

  if (formData.follower_count < 0) {
    errors.follower_count = '粉丝量不能为负数'
    isValid = false
  }

  if (formData.likes_count == null || formData.likes_count < 0) {
    errors.metrics = '请输入有效的点赞数'
    isValid = false
  }

  if (formData.saves_count == null || formData.saves_count < 0) {
    errors.metrics = '请输入有效的收藏数'
    isValid = false
  }

  if (formData.comments_count == null || formData.comments_count < 0) {
    errors.metrics = '请输入有效的评论数'
    isValid = false
  }

  if (!formData.title.trim()) {
    errors.title = '请输入标题'
    isValid = false
  }

  if (!formData.content.trim()) {
    errors.content = '请输入正文内容'
    isValid = false
  }

  if (!formData.visual_description.trim()) {
    errors.visual_description = '请输入视觉描述或使用 AI 生成'
    isValid = false
  } else if (parsedImageDescriptions.value.length > 0) {
    // 检查是否所有卡片都有内容
    const emptyCards = parsedImageDescriptions.value.filter(c => !c.content.trim())
    if (emptyCards.length === parsedImageDescriptions.value.length) {
      errors.visual_description = '请至少填写一张图片的视觉描述'
      isValid = false
    }
  }

  // 高赞评论改为可选，不再验证

  return isValid
}

async function handleSaveDraft() {
  if (!validate()) {
    alert('请完善表单中的必填项，确保所有标记为红色的字段都已正确填写')
    return
  }

  saving.value = true
  try {
    // Add image description metadata to draft data
    const draftData = {
      ...formData,
      // Add image description metadata
      image_descriptions: imageDescriptions.value,
      generated_image_indices: Object.keys(imageDescriptions.value).map(Number)
    }

    const response = await fetch('/api/analysis/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(draftData)
    })
    const result = await response.json()

    if (result.success) {
      emit('save-draft', result.data)
      // Reset unsaved flag after successful save
      hasUnsavedChanges.value = false
      // Show success toast, keep modal open
      showToast('草稿保存成功！您可以继续编辑或点击「开始 AI 分析」')
    } else {
      showToast(result.error || '保存失败，请重试', 'error')
    }
  } catch (e) {
    console.error('[AnalyzeConfirmModal] Failed to save draft:', e)
    showToast('保存失败，请检查网络连接', 'error')
  } finally {
    saving.value = false
  }
}

async function handleSubmit() {
  // 检查是否有未保存的内容
  if (hasUnsavedChanges.value) {
    confirm(
      '⚠️ 检测到未保存的内容修改\n\n' +
      '请先点击「保存草稿」按钮保存当前修改，然后再开始 AI 分析。'
    )
    // 阻止分析继续
    return
  }

  if (!validate()) {
    alert('请完善表单中的必填项，确保所有标记为红色的字段都已正确填写')
    return
  }

  const recordId = formData.record_id

  // 检查是否正在分析中
  if (analysisStore.isAnalyzing(recordId)) {
    alert('该笔记正在分析中，请稍候...')
    return
  }

  // 检查是否已有分析结果
  if (analysisStore.hasAnalysisResult(recordId)) {
    const confirmed = confirm(
      '该笔记已有分析结果。\n\n' +
      '⚠️ 点击「确定」将覆盖原有分析结果，生成新的分析。\n' +
      '点击「取消」保留原有结果。'
    )
    if (!confirmed) {
      return
    }
  }

  try {
    // 使用 store 的 submitAnalysis 方法（内部使用 SSE 流式处理）
    // 重置进度状态
    progressStep.value = ''
    progressMessage.value = ''

    const success = await analysisStore.submitAnalysis(formData, (step: string) => {
      progressStep.value = step
      // 根据步骤更新提示信息
      const stepMessages: any = { preparing: '正进行 AI 分析...', saving: '正在保存分析结果...', done: '分析完成！', error: '分析失败', failed: '连接失败' }
      progressMessage.value = stepMessages[step] || step
    })

    if (success) {
      emit('submit', formData)
      // Reset unsaved flag after successful submit
      hasUnsavedChanges.value = false
      // Close modal after successful analysis
      setTimeout(() => {
        emit('close')
        progressStep.value = ''
        progressMessage.value = ''
      }, 1500) // Wait briefly to show success message
    } else {
      alert('提交失败，请检查数据完整性')
      // 重置进度状态
      progressStep.value = ''
      progressMessage.value = ''
    }
  } catch (e) {
    console.error('[AnalyzeConfirmModal] Failed to submit:', e)
    alert('提交失败，请检查网络连接')
    // 重置进度状态
    progressStep.value = ''
    progressMessage.value = ''
  }
}

async function handleGenerateVisualDesc() {
  if (!props.record) return

  // 验证：至少选择一张图片
  if (selectedCount.value === 0) {
    alert('请先选择至少一张图片')
    return
  }

  generatingVisual.value = true
  try {
    // 找出已生成的图片索引（从 imageDescriptions 中获取）
    const alreadyGeneratedIndices = new Set(Object.keys(imageDescriptions.value).map(k => Number(k)))

    // 只为未生成的图片请求后端
    const newIndicesToGenerate = selectedImageIndices.value.filter(idx => !alreadyGeneratedIndices.has(idx))

    if (newIndicesToGenerate.length === 0) {
      alert('所选图片均已生成描述，无需重复生成')
      generatingVisual.value = false
      return
    }

    console.log(`[AnalyzeConfirmModal] Already generated: ${Array.from(alreadyGeneratedIndices)}, New to generate: ${newIndicesToGenerate}`)

    const response = await fetch('/api/analysis/visual-desc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        record_id: props.record.record_id,
        image_indices: newIndicesToGenerate  // 只发送新图片
      })
    })
    const result = await response.json()

    if (result.success && result.data?.descriptions) {
      const descriptionsMap = result.data.descriptions  // {index: description}

      // 为新生成的图片创建标记
      const markedDescriptionsList: string[] = []

      newIndicesToGenerate.forEach(idx => {
        const descContent = descriptionsMap[idx]
        if (!descContent) {
          console.warn(`[AnalyzeConfirmModal] No description for image index ${idx}`)
          return
        }

        // Generate unique ID per image: timestamp-random-index
        const uniqueDescId = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}-${idx}`

        // Add clear label for each image type
        const imageLabel = idx === -1 ? '【封面图】' : `【内容图${idx + 1}】`

        imageDescriptions.value[idx] = {
          id: uniqueDescId,
          content: descContent
        }

        // Add label + ID marker + description
        markedDescriptionsList.push(`<!-- DESC-${uniqueDescId} -->\n${imageLabel}\n${descContent}`)
      })

      // 追加新标记到现有描述（不删除已有内容）
      const newMarkedDescriptions = markedDescriptionsList.join('\n\n---\n\n')
      if (formData.visual_description) {
        formData.visual_description = formData.visual_description + '\n\n---\n\n' + newMarkedDescriptions
      } else {
        formData.visual_description = newMarkedDescriptions
      }

      console.log(`[AnalyzeConfirmModal] Generated ${newIndicesToGenerate.length} new descriptions, appended to form`)
    } else {
      alert(result.error || 'AI 生成失败，请手动输入')
    }
  } catch (e) {
    console.error('[AnalyzeConfirmModal] Failed to generate visual description:', e)
    alert('AI 生成失败，请检查网络连接')
  } finally {
    generatingVisual.value = false
  }
}

// ========== Helper Methods for Comments ==========

/**
 * Generate unique ID for comments/sub-comments
 */
function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
}

/**
 * Add a new top-level comment
 */
function addComment(): void {
  formData.top_comments.push({
    id: generateId(),
    content: '',
    likes: undefined,
    sub_comments: []
  })
}

/**
 * Add a new sub-comment to a parent comment
 */
function addSubComment(commentIndex: number): void {
  const comment = formData.top_comments[commentIndex]
  if (!comment.sub_comments) {
    comment.sub_comments = []
  }
  comment.sub_comments.push({
    id: generateId(),
    content: '',
    likes: undefined,
    is_blogger: false
  })
}

/**
 * Remove a top-level comment
 */
function removeComment(index: number): void {
  formData.top_comments.splice(index, 1)
}

/**
 * Remove a sub-comment from a parent comment
 */
function removeSubComment(commentIndex: number, subIndex: number): void {
  formData.top_comments[commentIndex].sub_comments?.splice(subIndex, 1)
}

// ========== 新增：图片描述清除方法 ==========

/**
 * Clear all image description metadata (e.g., when user clears form)
 */
function clearImageDescriptions() {
  imageDescriptions.value = {}
}

/**
 * Clear description for specific image index
 */
function clearImageDescription(idx: number) {
  delete imageDescriptions.value[idx]
}

/**
 * Add manual description card for an image
 */
function handleAddManualDescription() {
  if (!props.record) {
    alert('没有可用的图片')
    return
  }

  // Check if there are any images
  const hasCover = !!props.record.cover_image
  const hasContent = props.record.images && props.record.images.length > 0

  if (!hasCover && !hasContent) {
    alert('当前笔记没有可用图片')
    return
  }

  // If only one image, add directly
  if (hasCover && !hasContent) {
    addDescriptionCard(-1, '封面图')
    return
  }
  if (!hasCover && hasContent && props.record.images!.length === 1) {
    addDescriptionCard(0, '内容图1')
    return
  }

  // Multiple images: show selector modal
  selectedImageIndex.value = null
  showImageSelector.value = true
}

/**
 * Close the image selector modal
 */
function closeImageSelector() {
  showImageSelector.value = false
  selectedImageIndex.value = null
}

/**
 * Confirm the image selection and add description card
 */
function confirmImageSelection() {
  if (selectedImageIndex.value === null) return

  const selected = availableImages.value.find(img => img.index === selectedImageIndex.value)
  if (!selected) return

  addDescriptionCard(selected.index, selected.label)
  closeImageSelector()
}

/**
 * Create and add a new description card
 */
function addDescriptionCard(index: number, label: string) {
  // Check if description already exists
  if (imageDescriptions.value[index]) {
    if (!confirm('该图片已有描述，是否要添加新的描述卡片？')) {
      return
    }
  }

  // Generate unique ID
  const uniqueDescId = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}-${index}`

  // Store in metadata
  imageDescriptions.value[index] = {
    id: uniqueDescId,
    content: ''
  }

  // Build the new description entry with proper label
  const imageLabel = index === -1 ? '【封面图】' : `【内容图${index + 1}】`
  const newEntry = `<!-- DESC-${uniqueDescId} -->\n${imageLabel}\n`

  // Append to existing visual_description
  if (formData.visual_description.trim()) {
    formData.visual_description = formData.visual_description + '\n\n---\n\n' + newEntry
  } else {
    formData.visual_description = newEntry
  }

  console.log('[AnalyzeConfirmModal] Added manual description card:', { index, label, uniqueDescId })
}

function handleClose(skipConfirm = false) {
  // Only check for unsaved changes if not explicitly skipping confirmation
  if (!skipConfirm && hasUnsavedChanges.value) {
    if (!confirm('确定要关闭吗？未保存的内容将会丢失。')) {
      return
    }
  }
  emit('close')
}

// ========== 新增：图片选择方法 ==========

/**
 * 检查内容图是否被选中
 */
function isContentImageSelected(idx: number): boolean {
  return selectedImageIndices.value.includes(idx)
}

/**
 * 切换内容图选中状态
 */
function toggleContentImage(idx: number): void {
  const index = selectedImageIndices.value.indexOf(idx)
  if (index > -1) {
    selectedImageIndices.value.splice(index, 1)
  } else {
    selectedImageIndices.value.push(idx)
  }
}

/**
 * 全选内容图
 */
function selectAllContent(): void {
  if (!props.record?.images) return
  props.record.images.forEach((_, idx) => {
    if (!selectedImageIndices.value.includes(idx)) {
      selectedImageIndices.value.push(idx)
    }
  })
}

/**
 * 清空内容图选择
 */
function clearAllContent(): void {
  selectedImageIndices.value = selectedImageIndices.value.filter(i => i === -1)
}

/**
 * 处理封面图加载失败
 */
function handleCoverError(): void {
  console.warn('[AnalyzeConfirmModal] Cover image failed to load:', props.record?.cover_image)
  coverLoadError.value = true
}

/**
 * 处理内容图加载失败
 */
function handleContentError(idx: number): void {
  const imgUrl = props.record?.images?.[idx]
  console.warn(`[AnalyzeConfirmModal] Content image ${idx} failed to load:`, imgUrl)
  contentLoadErrors.value.add(idx)
}

/**
 * 检查本地是否有图片
 */
async function checkLocalImages() {
  if (!props.record) return

  try {
    const { checkReferenceImages } = await import('@/api')
    const result = await checkReferenceImages(props.record.record_id)

    // 先清空数据中的图片链接（可能是过期的飞书图片）
    if (props.record) {
      props.record.images = []
    }

    // 只使用本地存在的图片
    if (result.exists && result.images.length > 0) {
      if (props.record) {
        props.record.images = result.images
      }
    }

    hasCheckedLocal.value = true
    console.log('[AnalyzeConfirmModal] Local images check result:', result)
  } catch (e) {
    console.error('[AnalyzeConfirmModal] Failed to check local images:', e)
    hasCheckedLocal.value = true
  }
}
</script>

<style scoped>
/* Toast 通知 */
.toast-notification {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 2000;
  min-width: 280px;
  max-width: 420px;
}

.toast-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.toast-error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toast-message {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

/* Toast 动画 */
.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 1, 1);
}

.toast-enter-from {
  opacity: 0;
  transform: translate(-50%, -16px);
}

.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -8px);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.confirm-modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .confirm-modal,
.modal-leave-to .confirm-modal {
  transform: scale(0.9) translateY(-20px);
}

/* Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e6e3;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #999;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f8f7f5;
  color: #666;
}

/* Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.form-section {
  margin-bottom: 24px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #ff2442;
  display: inline-block;
}

.form-group {
  margin-bottom: 16px;
  position: relative;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
}

.form-label.required::after {
  content: ' *';
  color: #ff2442;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  transition: all 0.2s;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #ff2442;
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.1);
}

.form-input.error,
.form-select.error,
.form-textarea.error {
  border-color: #ff2442;
}

.form-error {
  display: block;
  font-size: 12px;
  color: #ff2442;
  margin-top: 4px;
}

.char-count {
  position: absolute;
  right: 12px;
  bottom: -20px;
  font-size: 11px;
  color: #999;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

/* Metrics Inputs */
.metrics-inputs {
  display: flex;
  gap: 12px;
}

.metric-input {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8f7f5;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #e8e6e3;
}

.metric-label {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.metric-input .form-input {
  flex: 1;
  min-width: 60px;
  border: none;
  background: transparent;
  padding: 4px 8px;
  font-size: 14px;
}

/* Visual Description */
.visual-desc-wrapper {
  position: relative;
}

.ai-generate-btn {
  position: absolute;
  right: 8px;
  bottom: 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #ff2442;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.ai-generate-btn:hover:not(:disabled) {
  background: #e61e3a;
}

.ai-generate-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.ai-generate-btn svg.spin {
  animation: spin 1s linear infinite;
}

.progress-message {
  margin-left: 8px;
  font-size: 12px;
  color: white;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ========== Comments ========== */

/* Legacy styles - removed in favor of Enhanced Comments below */

/* Footer */
.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #e8e6e3;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f8f7f5;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background: #e8e6e3;
}

.btn-primary {
  background: #ff2442;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #e61e3a;
}

.btn-primary svg.spin {
  animation: spin 1s linear infinite;
}

/* ========== 图片选择区域 ========== */
.image-selection-area {
  margin-bottom: 16px;
}

.image-group {
  margin-bottom: 16px;
}

.group-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

/* 图片复选框 */
.image-checkbox {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.image-checkbox.checked {
  border-color: #ff2442;
  background: #ffeee8;
}

.image-checkbox:hover {
  transform: scale(1.05);
}

.image-checkbox input[type="checkbox"] {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 16px;
  height: 16px;
  cursor: pointer;
  z-index: 1;
}

.image-checkbox img {
  display: block;
  object-fit: cover;
  border-radius: 4px;
}

/* 封面图尺寸 */
.cover-group .image-checkbox {
  display: inline-flex;
}

.cover-group .image-checkbox img {
  width: 80px;
  height: 80px;
}

/* 内容图网格 */
.content-images-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 8px;
}

.content-images-grid .image-checkbox {
  display: flex;
  flex-direction: column;
  padding: 6px;
}

.content-images-grid .image-checkbox img {
  width: 60px;
  height: 60px;
}

.image-label {
  font-size: 11px;
  color: #666;
  text-align: center;
  margin-top: 2px;
}

.load-error-icon {
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.image-checkbox.error {
  opacity: 0.7;
}

.image-placeholder {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 4px;
  color: #999;
}

.image-error-placeholder {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff0f0;
  border-radius: 4px;
  color: #ff2442;
}

.image-error-placeholder .error-text {
  font-size: 10px;
  text-align: center;
  padding: 4px;
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  gap: 8px;
}

.quick-actions button {
  padding: 4px 12px;
  font-size: 12px;
  border: 1px dashed #ddd;
  background: transparent;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-actions button:hover {
  border-color: #ff2442;
  color: #ff2442;
}

/* 操作栏 */
.visual-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f7f5;
  border-radius: 8px;
  margin-bottom: 16px;
  gap: 12px;
}

.action-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.selection-count {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
}

/* 模式切换按钮 */
.mode-toggle {
  display: inline-flex;
  background: #e8e6e3;
  border-radius: 6px;
  padding: 2px;
  gap: 2px;
}

.mode-btn {
  padding: 4px 12px;
  font-size: 12px;
  border: none;
  background: transparent;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.mode-btn:hover {
  color: #333;
}

.mode-btn.active {
  background: white;
  color: #ff2442;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.btn-generate {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #ff2442;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-generate:hover:not(:disabled) {
  background: #e61e3a;
}

.btn-generate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-generate svg.spin {
  animation: spin 1s linear infinite;
}

/* 无图片提示 */
.no-images-message {
  padding: 16px;
  background: #fff8f0;
  border: 1px solid #ffcc00;
  border-radius: 8px;
  margin-bottom: 16px;
  text-align: center;
}

.no-images-message p {
  margin: 4px 0;
  font-size: 13px;
  color: #666;
}

/* 响应式：移动端调整为2列 */
@media (max-width: 480px) {
  .content-images-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  /* Mobile comments layout */
  .sub-comments-grid {
    grid-template-columns: 1fr;
  }

  .comment-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .add-sub-comment-btn {
    justify-content: center;
  }

  .likes-wrapper {
    justify-content: center;
  }
}

/* ========== Image Badge Styles ========== */
.image-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border: 2px solid white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
  z-index: 2;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.image-badge.generated {
  background: #52c41a;
}

.image-badge.missing {
  background: #faad14;
}

/* ========== 图片描述卡片样式 ========== */
.image-desc-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.image-desc-card {
  background: white;
  border: 1px solid #e8e6e3;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.image-desc-card:hover {
  border-color: #ddd;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.image-desc-card.card-error {
  border-color: #ff2442;
}

.image-desc-card.card-error .card-textarea {
  border-color: #ff2442;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #f8f7f5;
  border-bottom: 1px solid #e8e6e3;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-thumb {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #e8e6e3;
}

.card-thumb-placeholder {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8e6e3;
  border-radius: 6px;
  color: #999;
}

.card-label {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.card-badge {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: white;
}

.card-badge.generated {
  background: #52c41a;
}

.card-badge.missing {
  background: #faad14;
}

.card-delete-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #999;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.card-delete-btn:hover {
  background: #ffeee8;
  color: #ff2442;
}

/* 卡片内容 */
.card-textarea {
  width: 100%;
  padding: 12px 14px;
  border: none;
  border-radius: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #333;
  font-family: inherit;
  resize: vertical;
  min-height: 80px;
  background: white;
}

.card-textarea:focus {
  outline: none;
  background: #fafafa;
}

.card-textarea::placeholder {
  color: #bbb;
}

/* 空状态提示 */
.empty-cards-hint {
  padding: 24px;
  background: #f8f7f5;
  border: 1px dashed #ddd;
  border-radius: 12px;
  text-align: center;
}

.empty-cards-hint p {
  margin: 0;
  font-size: 13px;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* 手动添加描述按钮 */
.manual-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: #ff2442;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.manual-add-btn:hover {
  background: #e61e3a;
  transform: scale(1.05);
}

/* 添加手动描述包装器（有卡片时显示） */
.add-manual-desc-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px;
  background: #f8f7f5;
  border-radius: 8px;
  margin-top: 12px;
}

.add-manual-desc-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #ff2442;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.add-manual-desc-btn:hover {
  background: #e61e3a;
  transform: scale(1.05);
}

.add-desc-hint {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

/* ========== Enhanced Comments Styles ========== */

/* Comments list - more generous spacing */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Comment Card - main container */
.comment-card {
  background: #faf9f7;
  border: 1px solid #e8e6e3;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.comment-card:hover {
  border-color: #ddd;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Comment Card Header */
.comment-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #e8e6e3;
}

.comment-number {
  font-size: 12px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Remove comment button */
.remove-comment-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #bbb;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.remove-comment-btn:hover {
  background: #ffeee8;
  color: #ff2442;
}

/* Comment Content */
.comment-content {
  padding: 16px;
}

.comment-textarea {
  width: 100%;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  padding: 12px 14px;
  background: white;
  transition: all 0.2s;
}

.comment-textarea:focus {
  outline: none;
  border-color: #ff2442;
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.08);
}

/* Comment Footer - action bar */
.comment-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px 12px 16px;
  gap: 16px;
}

/* Add sub-comment button */
.add-sub-comment-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid #e0dedb;
  background: white;
  color: #666;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.add-sub-comment-btn:hover {
  border-color: #ff2442;
  color: #ff2442;
  background: #ffeee8;
}

/* Likes wrapper */
.likes-wrapper {
  display: flex;
  align-items: center;
}

.likes-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e0dedb;
  border-radius: 6px;
  color: #666;
  font-size: 13px;
}

.likes-label svg {
  color: #ffb347;
  flex-shrink: 0;
}

.likes-input {
  width: 60px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  text-align: right;
}

.likes-input:focus {
  outline: none;
}

.likes-input::placeholder {
  color: #bbb;
  font-weight: 400;
}

/* Sub-comments Section */
.sub-comments-section {
  border-top: 1px solid #e8e6e3;
  background: #fff;
}

.sub-comments-header {
  padding: 10px 16px;
  background: #f5f4f2;
}

.sub-comments-title {
  font-size: 11px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Sub-comments Grid */
.sub-comments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
  padding: 12px;
}

/* Sub-comment Card */
.sub-comment-card {
  background: #faf9f7;
  border: 1px solid #e8e6e3;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.sub-comment-card:hover {
  border-color: #ddd;
}

/* Sub-comment Header */
.sub-comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: #f5f4f2;
}

/* Blogger toggle switch */
.blogger-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: #e8e6e3;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  color: #999;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
}

.blogger-toggle input[type="checkbox"] {
  display: none;
}

.toggle-indicator {
  width: 12px;
  height: 12px;
  border: 1.5px solid #bbb;
  border-radius: 2px;
  background: white;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.blogger-toggle.active {
  background: #ff2442;
  color: white;
}

.blogger-toggle.active .toggle-indicator {
  background: white;
  border-color: white;
}

.blogger-toggle.active .toggle-indicator::after {
  content: '✓';
  font-size: 9px;
  color: #ff2442;
  font-weight: bold;
}

.toggle-label {
  line-height: 1;
}

/* Remove sub-comment button */
.remove-sub-comment-btn {
  width: 22px;
  height: 22px;
  border: none;
  background: transparent;
  color: #bbb;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.remove-sub-comment-btn:hover {
  background: #ffeee8;
  color: #ff2442;
}

/* Sub-comment textarea */
.sub-comment-textarea {
  width: 100%;
  border: none;
  border-radius: 0;
  font-size: 13px;
  line-height: 1.5;
  padding: 10px 12px;
  background: transparent;
  min-height: 60px;
  resize: vertical;
}

.sub-comment-textarea:focus {
  outline: none;
  background: white;
}

/* Sub-comment footer */
.sub-comment-footer {
  display: flex;
  justify-content: flex-end;
  padding: 6px 10px;
  border-top: 1px solid #e8e6e3;
}

.mini-likes {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

.mini-likes svg {
  color: #ffb347;
}

.mini-likes input {
  width: 45px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 500;
  color: #666;
  text-align: right;
}

.mini-likes input:focus {
  outline: none;
}

/* Add comment button */
.add-comment-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: 1px dashed #ccc;
  background: transparent;
  color: #999;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.25s;
  width: 100%;
  justify-content: center;
  font-weight: 500;
}

.add-comment-btn:hover {
  border-color: #ff2442;
  color: #ff2442;
  background: #ffeee8;
}

/* ========== 修改警告横幅 ========== */
.modification-warning-banner {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #fff8f0 0%, #ffede6 100%);
  border: 2px solid #ff9800;
  border-radius: 12px;
  margin-bottom: 24px;
  animation: warning-pulse 2s ease-in-out infinite;
}

@keyframes warning-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 152, 0, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(255, 152, 0, 0);
  }
}

.warning-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ff9800;
  color: white;
  border-radius: 50%;
  animation: icon-shake 0.5s ease-in-out;
}

@keyframes icon-shake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}

.warning-content {
  flex: 1;
}

.warning-title {
  font-size: 15px;
  font-weight: 700;
  color: #e65100;
  margin-bottom: 6px;
}

.warning-message {
  font-size: 13px;
  color: #bf360c;
  margin-bottom: 6px;
  line-height: 1.5;
}

.warning-hint {
  font-size: 12px;
  color: #e65100;
  opacity: 0.8;
  font-style: italic;
}

/* ========== 字段修改状态指示器 ========== */
.modified-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  background: #ff5722;
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
  margin-left: 8px;
  animation: badge-appear 0.3s ease-out;
}

@keyframes badge-appear {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.field-modified {
  position: relative;
}

.field-modified::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 8px;
  width: 4px;
  height: calc(100% - 16px);
  background: #ff5722;
  border-radius: 2px;
  animation: slide-in-left 0.3s ease-out;
}

@keyframes slide-in-left {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* ========== 图片选择弹窗样式 ========== */
.image-selector-modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  animation: selector-appear 0.25s ease-out;
}

@keyframes selector-appear {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e8e6e3;
  background: linear-gradient(135deg, #ff2442 0%, #ff6b6b 100%);
}

.selector-header .selector-title {
  font-size: 16px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.selector-header .close-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.selector-header .close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.selector-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.selector-hint {
  font-size: 13px;
  color: #666;
  margin: 0 0 16px 0;
  text-align: center;
  font-style: italic;
}

.selector-image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 12px;
}

.selector-image-card {
  background: white;
  border: 2px solid #e8e6e3;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.selector-image-card:hover {
  border-color: #ff2442;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 36, 66, 0.15);
}

.selector-image-card.selected {
  border-color: #ff2442;
  background: #ffeee8;
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.2);
}

.selector-image-card.has-desc {
  border-color: #52c41a;
}

.selector-image-card.has-desc:hover {
  border-color: #3aae38;
}

.selector-thumb-wrapper {
  position: relative;
  width: 100%;
  padding-top: 100%;
  background: #f5f5f5;
}

.selector-thumb {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.selector-thumb-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
}

.selector-has-desc-badge {
  position: absolute;
  top: 6px;
  left: 6px;
  width: 20px;
  height: 20px;
  background: #52c41a;
  border: 2px solid white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.selector-selected-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  background: #ff2442;
  border: 2px solid white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  animation: badge-pop 0.2s ease-out;
}

@keyframes badge-pop {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.selector-label {
  padding: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #333;
  text-align: center;
  background: #fafafa;
  border-top: 1px solid #e8e6e3;
}

.selector-image-card.selected .selector-label {
  background: #ffeee8;
  color: #ff2442;
}

.selector-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #e8e6e3;
  background: #f8f7f5;
}

.selector-footer .btn {
  padding: 10px 20px;
  font-size: 14px;
}

/* Responsive for selector modal */
@media (max-width: 480px) {
  .selector-image-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
