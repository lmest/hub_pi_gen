#pragma once

typedef enum cbf_status_s
{
    CBF_OK = 0, /**< Opera��o realizada com sucesso */
    CBF_FULL,   /**< Buffer circular cheio */
    CBF_EMPTY,  /**< Buffer circular vazio */
} cbf_status_t;

typedef struct cbf_s
{
    volatile uint16_t prod; /**< Indicador da posi��o de produ��o no buffer circular */
    volatile uint16_t cons; /**< Indicador da posi��o de consumo no buffer circular */
    uint16_t size;          /**< Tamanho total do buffer circular */
    uint8_t* buffer;        /**< Ponteiro para a �rea de dados do buffer circular (alocado pelo usu�rio) */
} cbf_t;


/**
 @brief Retorna a quantidade de bytes dispon�vel para consumo num buffer circular.
 @param[in] cb - ponteiro para o buffer circular.
 @return quantidade de bytes dispon�vel para consumo
*/
uint16_t cbf_bytes_available(cbf_t* cb);
/**
 @brief Esvazia um buffer circular.
 @param[in] cb - ponteiro para o buffer circular.
 @return ver @ref cbf_status_s
*/
cbf_status_t cbf_flush(cbf_t* cb);
/**
 @brief Retira um byte do buffer circular.
 @param[in] cb - ponteiro para o buffer circular.
 @param[out] c - ponteiro para o destino do dado (previamente alocado).
 @return ver @ref cbf_status_s
*/
cbf_status_t cbf_get(cbf_t* cb, uint8_t* c);
/**
 @brief Reinicializa um buffer circular, caso seja necess�rio.
 @param[in] cb - ponteiro para o buffer circular.
 @param[in] area - buffer previamente alocado que ser� usado para armazenamento do conte�do do buffer circular.
 @param[in] size - tamanho da �rea de dados apontada por @p area.
 @return ver @ref cbf_status_s
*/
cbf_status_t cbf_init(cbf_t* cb, uint8_t* area, uint16_t size);
/**
 @brief Coloca um byte no buffer circular.
 @param[in] cb - ponteiro para o buffer circular.
 @param[in] c - byte a ser adicionado ao buffer circular.
 @return ver @ref cbf_status_s
*/
cbf_status_t cbf_put(cbf_t* cb, uint8_t c);
